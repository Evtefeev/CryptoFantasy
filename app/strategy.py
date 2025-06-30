from abc import ABC, abstractmethod
import pickle
import random
import uuid
from actions import RandomCharacterGenerator, StrategyGame, Game
import logging

logging.basicConfig(level=logging.DEBUG)


class Storage(ABC):
    @abstractmethod
    def save(self, type: str, label: str, obj: bytes):
        pass

    @abstractmethod
    def get(self, type: str, label: str) -> bytes:
        pass


class MemoryStorage(Storage):
    def __init__(self):
        self.data = {}

    def save(self, type: str, label: str, obj: bytes):
        if type not in self.data:
            self.data[type] = {}
        self.data[type][str(label)] = obj  # ключ — строка

    def get(self, type: str, label: str) -> bytes:
        return self.data.get(type, {}).get(str(label), None)


STORAGE = MemoryStorage()


class Player:
    storage_type = 'player'

    def __init__(self, uid=None, storage: Storage = STORAGE):
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
        st = self.storage
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
            return cls(storage, uid)
        obj = pickle.loads(raw)
        obj.storage = storage  # восстанавливаем storage (не сериализуем его)
        return obj


class Strategy:

    CARDS_NUMBER = 6
    MIN_ENERGY = 0.05

    def __init__(self, storage: Storage = STORAGE, users_ids=[], new=True):
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
                         defender.cards[opponent_card])
        if opponent_card in defender.active_cards and defender.cards[opponent_card].health <= 0:
            defender.active_cards.remove(opponent_card)
        attacker.save()
        defender.save()

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


class StrategyBot(Strategy):

    def __init__(self, uid, storage=STORAGE):
        self.botuid = str(uid)+'-bot'
        super().__init__(storage, [uid, self.botuid])
        self.user = self.players[uid]
        self.bot = self.players[self.botuid]
        self.generateCards()

    def userAttack(self, uid, my_card_num, opponent_card_num):
        before = self.getOpponentCardInfo(opponent_card_num)
        self.attackOpponent(my_card_num, opponent_card_num)
        after = self.getOpponentCardInfo(opponent_card_num)
        user = self.getUserCardInfo(uid, my_card_num)
        return before, after, user

    def getStatus(self, uid):
        if len(self.bot.active_cards) == 0:
            return 'Victory!'
        if len(self.user.active_cards) == 0:
            return 'lose!'
        return None

    def waitAttack(self, uid):
        self.increaseOpponentEnergy()
        user_card_num = self.getRandomActiveUserCardNumber()
        opponent_card_num = self.getRandomActiveOpponentCardNumber()
        self.attackUser(user_card_num, opponent_card_num)
        opponent_info = self.getOpponentCardInfo(opponent_card_num)
        user_info = self.getUserCardInfo(uid, user_card_num)
        status = self.getStatus(uid)
        return opponent_info, user_info, status or "turn"

    def attackOpponent(self, user_card, opponent_card):
        self.increaseUserEnergy()
        self.attack(self.user, self.bot, user_card, opponent_card)

    def attackUser(self, user_card, opponent_card):
        self.attack(self.bot, self.user, opponent_card, user_card)

    def getUserCards(self):
        return self.user.cards

    def getUserCardsInfo(self, uid):
        return self._getUserCardsInfo(self.user)

    def getUserCardInfo(self, uid, num):
        return self._getUserCardInfo(self.user, num)

    def getOpponentCardInfo(self, num):
        return self._getUserCardInfo(self.bot, num)

    def getRandomActiveUserCardNumber(self):
        if not self.user.active_cards:
            return None
        return random.choice(self.user.active_cards)

    def getRandomActiveOpponentCardNumber(self, ready=True):
        if not self.bot.active_cards:
            return None
        if ready:
            ready_cards = self.getReadyComputerCards()
            if ready_cards:
                return random.choice(ready_cards).card_number
            return None
        return random.choice(self.bot.active_cards)

    def increaseUserEnergy(self):
        self._increaseUserEnergy(self.user)

    def increaseOpponentEnergy(self):
        self._increaseUserEnergy(self.bot)

    def getReadyComputerCards(self):
        return [
            card for card in self.bot.cards
            if card.energy > 0.9 and card.card_number in self.bot.active_cards
        ]

    def isReady(self):
        return bool(self.bot.active_cards and self.user.active_cards)


pvp_strategies = []


def StrategyPvPConnector(user_id):
    if len(pvp_strategies) > 0:
        game: Strategy = pvp_strategies.pop()
        game.players[user_id] = Player()
        game.generateCards()
    else:
        game = StrategyPvPGame(user_id)
        pvp_strategies.append(game)
    logging.debug("Player connected")
    return game


def StrategyPvP(user_id):
    return StrategyPvPConnector(user_id)


class StrategyPvPGame(Strategy):
    def __init__(self, user_id):
        super().__init__()
        self.players[user_id] = Player()
        self.last_turn = None
        self.opponents = {}

    def isReady(self):
        if len(self.players) == 2 and self.opponents == {}:
            player1, player2 = self.players.keys()
            self.opponents[player1] = player2
            self.opponents[player2] = player1
        return len(self.players) == 2

    def getUserCardsInfo(self, user_id):
        return self._getUserCardsInfo(self.players[user_id])

    def attackUser(self, user_card, opponent_card, user_id, opponent_id):
        self.attack(
            self.players[user_id], self.players[opponent_id], user_card, opponent_card)

    def userAttack(self, uid, my_card_num, opponent_card_num):
        if not self.isReady():
            raise Exception("Game not ready")
        if self.last_turn == uid:
            raise Exception("Not your turn!")
        strategy = self
        before = strategy.getOpponentCardInfo(uid, opponent_card_num)
        strategy.attackOpponent(uid, my_card_num, opponent_card_num)
        after = strategy.getOpponentCardInfo(uid, opponent_card_num)
        user = strategy.getUserCardInfo(uid, my_card_num)
        self.last_turn = uid
        return before, after, user

    def getUserCardInfo(self, uid, num):
        return self._getUserCardInfo(self.players[uid], num)

    def getOpponentCardInfo(self, uid, num):
        return self._getUserCardInfo(self.players[self.getOpponent(uid)], num)

    def getOpponent(self, uid):
        return self.opponents[uid]

    def attackOpponent(self, uid, user_card, opponent_card):
        user = self.players[uid]
        opponent = self.players[self.getOpponent(uid)]
        self.increaseUserEnergy(user)
        self.opponent_card_num = user_card
        self.user_card_num = opponent_card
        self.attack(user, opponent, user_card, opponent_card)
        self.last_turn = uid

    def increaseUserEnergy(self, user):
        return super()._increaseUserEnergy(user)

    def waitAttack(self, uid):
        if self.last_turn and self.last_turn != uid:
            player = self.players[uid]
            strategy = self
            opponent_info = strategy.getOpponentCardInfo(
                uid, self.opponent_card_num)
            user_info = strategy._getUserCardInfo(player, self.user_card_num)
            status = strategy.getStatus(uid)
            if not status:
                status = "turn" if self.last_turn != uid else "waiting"
            return opponent_info, user_info, status
        return None, None, "waiting"

    def getStatus(self, uid):
        user: Player = self.players[uid]
        opponent: Player = self.players[self.getOpponent(uid)]
        if len(opponent.active_cards) == 0:
            return 'Victory!'
        if len(user.active_cards) == 0:
            return 'lose!'
        return None

    def getTurn(self, uid):
        players = list(self.players.keys())
        return players[0] == uid
