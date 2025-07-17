import copy
import logging
import pickle
import uuid
from flask import json
from app.actions import Game, StrategyGame
from app.helpers import StrategyStorage
import app.conf as conf
from app.charcters import RandomCharacterGenerator
from app.conf import STORAGE
from app.storages import Storage

logging.basicConfig(level=logging.DEBUG)

STORAGE = conf.STORAGE


class Player:
    storage_type = 'player'

    def __init__(self, uid=None, storage: Storage = STORAGE):
        if not isinstance(storage, Storage):
            raise TypeError("storage must be a Storage object")
        self.storage = storage
        self.uid = uid or str(uuid.uuid4())
        self.cards = []
        self.active_cards = []

    def generateCards(self):
        if not self.cards:
            self.cards = self.__generateCards()
            self.__generateCardsNumbers()

    def __generateCards(self):
        return [RandomCharacterGenerator.generate_random_character()
                for _ in range(Strategy.CARDS_NUMBER)]

    def __generateCardsNumbers(self):
        self.active_cards.clear()
        for n, card in enumerate(self.cards):
            card.set_card_number(n)
            self.active_cards.append(n)

    def save(self):
        st = copy.copy(self.storage)
        self.storage = None
        raw = pickle.dumps(self)
        self.storage = st
        logging.debug(st)
        logging.debug(self.storage)
        self.storage.save(self.storage_type, self.uid, raw)

    @classmethod
    def load(cls, storage: Storage, uid: str):
        raw = storage.get(cls.storage_type, uid)
        if raw is None:
            return cls(uid, storage)
        obj = pickle.loads(raw)
        obj.storage = storage  # восстанавливаем storage (не сериализуем его)
        return obj


class Strategy:
    CHEAT_MODE = conf.ENABLE_CHEAT
    CARDS_NUMBER = 6
    MIN_ENERGY = 0.05
    SKIP_FIELDS = ['storage', 'game', 'user', 'bot']

    def __init__(self, storage: Storage = STORAGE, users_ids=[], new=True):
        self.uid = None
        if not isinstance(storage, Storage):
            raise TypeError("storage must be a Storage object")
        self.storage = storage
        self.players = {}

        for uid in users_ids:
            if new:
                self.players[uid] = Player(uid)
            else:
                self.players[uid] = Player.load(storage, uid)
        self.game = StrategyGame()
        self.game.damage_factor = 10

    def attack(self, attacker: Player, defender: Player, user_card, opponent_card):
        self.game.attack(attacker.cards[user_card],
                         defender.cards[opponent_card],
                         self.CHEAT_MODE
                         )
        if opponent_card in defender.active_cards and defender.cards[opponent_card].health <= 0:
            defender.active_cards.remove(opponent_card)
        attacker.save()
        defender.save()
        self.save()

    def generateCards(self):
        for player in self.players.values():
            player.generateCards()
            player.save()

    def _getUserCardsInfo(self, user: Player):
        return [card.info() for card in user.cards]

    def _getUserCardInfo(self, user: Player, num):
        return user.cards[num].info()

    def getUserCardsInfo(self, user: Player):
        return self._getUserCardsInfo(user)

    def _increaseUserEnergy(self, user: Player):
        for card in user.cards:
            if card.card_number in user.active_cards and card.energy < 1:
                card.energy *= Game.ENERGY_DECREASE_FACTOR / 3
            card.energy = min(max(card.energy, self.MIN_ENERGY), 1)
        user.save()

    def to_json(self):
        result = {}
        for k, v in self.__dict__.items():
            if k not in self.SKIP_FIELDS:
                if k == 'players':
                    [p.save() for p in v.values()]
                    v = [p for p in v.keys()]
                result[k] = v
                logging.debug(f"{k}: {v}")
        return json.dumps(result)

    def from_json(self, json_str):
        data = json.loads(json_str)
        for k, v in data.items():
            if k == 'players':
                # You can adjust this if you need to reconstruct player objects
                players = v.copy()
                v = {}
                for p in players:
                    v[p] = Player.load(self.storage, p)
            setattr(self, k, v)

    def _is_json_serializable(self, v):
        try:
            json.dumps(v)
            return True
        except (TypeError, OverflowError):
            return False

    def save(self):
        StrategyStorage(self.storage).save_strategy(self, self.uid)
        
        
    def recover(self, uid):
        pass
