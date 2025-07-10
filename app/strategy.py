import random

import logging
from app.base_strategy import Player, Strategy
from app.helpers import StrategyStorage

import app.conf as conf

logging.basicConfig(level=logging.DEBUG)

STORAGE = conf.STORAGE


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


def StrategyPvPConnector(user_id, storage=conf.STORAGE):
    PVP_STRATEGIES_PREFIX = 'PVPStrategiesQueue'

    prev_strategy_id = storage.get(
        PVP_STRATEGIES_PREFIX, PVP_STRATEGIES_PREFIX)
    print(prev_strategy_id)
    if prev_strategy_id and prev_strategy_id != -1:
        game: Strategy = StrategyStorage(storage).get_strategy(
            prev_strategy_id, StrategyPvPGame)
        game.players[user_id] = Player(user_id, storage)
        game.generateCards()
        for p in game.players:
            game.players[p].save()
        game.prepare()
        StrategyStorage(storage).save_strategy(game, prev_strategy_id)
        storage.save(
            PVP_STRATEGIES_PREFIX, PVP_STRATEGIES_PREFIX, -1)
    else:
        game = StrategyPvPGame(user_id, storage)
        game.players[user_id].save()

        strategy_id = StrategyStorage(storage).save_strategy(game)
        storage.save(
            PVP_STRATEGIES_PREFIX, PVP_STRATEGIES_PREFIX, strategy_id)
    logging.debug("Player connected")
    return game


def StrategyPvP(user_id, storage=conf.STORAGE):
    return StrategyPvPConnector(user_id, storage)


class StrategyPvPGame(Strategy):
    def __init__(self, user_id=None, storage=conf.STORAGE):
        super().__init__()
        if user_id:
            self.players[user_id] = Player(user_id, storage)
        self.last_turn = None
        self.opponents = {}

    def prepare(self):
        if len(self.players) == 2 and self.opponents == {}:
            player1, player2 = self.players.keys()
            self.opponents[player1] = player2
            self.opponents[player2] = player1

    def isReady(self):
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
        self.save()
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
