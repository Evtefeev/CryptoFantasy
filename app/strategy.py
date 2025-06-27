import random
from actions import RandomCharacterGenerator, StrategyGame, Game
import logging

logging.basicConfig(level=logging.DEBUG)


class Player:
    def __init__(self):
        self.cards = []
        self.active_cards = []

    def generateCards(self):
        self.cards = self.__genetrateCards()
        self.__generateCardsNumbers()

    def __genetrateCards(self):
        return [RandomCharacterGenerator.generate_random_character()
                for _ in range(Strategy.CARDS_NUMBER)]

    def __generateCardsNumbers(self):
        self.active_cards.clear()
        self.active_cards.clear()

        for n, card in enumerate(self.cards):
            card.set_card_number(n)
            self.active_cards.append(n)


class Strategy:

    CARDS_NUMBER = 6
    MIN_ENERGY = 0.05

    def __init__(self):
        self.players = {}
        self.game = StrategyGame()
        self.game.damage_factor = 10

    def attack(self, attacker: Player, defender: Player, user_card, opponent_card):
        self.game.attack(
            attacker.cards[user_card], defender.cards[opponent_card])
        if opponent_card in defender.active_cards and defender.cards[opponent_card].health <= 0:
            defender.active_cards.remove(opponent_card)

    def generateCards(self):
        for player in self.players.values():
            player.generateCards()

    def _getUserCardsInfo(self, user):
        return [card.info() for card in user.cards]

    def _getUserCardInfo(self, user, num):
        return user.cards[num].info()


class StrategyBot(Strategy):

    def __init__(self):
        super().__init__()
        self.players["user"] = Player()
        self.players["bot"] = Player()
        self.user = self.players["user"]
        self.bot = self.players["bot"]
        self.generateCards()

    def userAttack(self, my_card_num, opponent_card_num):
        strategy = self
        before = strategy.getOpponentCardInfo(opponent_card_num)
        strategy.attackOpponent(my_card_num, opponent_card_num)
        after = strategy.getOpponentCardInfo(opponent_card_num)
        user = strategy.getUserCardInfo(my_card_num)
        return before, after, user

    def getStatus(self):
        strategy = self
        opponent_card_num = strategy.getRandomActiveOpponentCardNumber()
        if opponent_card_num == None:
            return 'Victory!'
        user_card_num = strategy.getRandomActiveUserCardNumber()
        if user_card_num == None:
            return 'lose!'
        return None

    def computerAttack(self):
        strategy = self
        user_card_num = strategy.getRandomActiveUserCardNumber()
        opponent_card_num = strategy.getRandomActiveOpponentCardNumber()
        strategy.attackUser(user_card_num, opponent_card_num)
        opponent_info = strategy.getOpponentCardInfo(opponent_card_num)
        user_info = strategy.getUserCardInfo(user_card_num)
        status = strategy.getStatus()
        return opponent_info, user_info, status

    def attackOpponent(self, user_card, opponent_card):
        self.increaseUserEnergy()
        self.attack(self.user, self.bot, user_card, opponent_card)

    def attackUser(self, user_card, opponent_card):
        self.increaseOpponentEnergy()
        self.attack(self.bot, self.user, user_card, opponent_card)

    def getUserCards(self):
        return self.user.cards

    def getUserCardsInfo(self):
        return self._getUserCardsInfo(self.user)

    def getUserCardInfo(self, num):
        return self._getUserCardInfo(self.user, num)

    def getOpponentCardInfo(self, num):
        return self._getUserCardInfo(self.bot, num)

    def getRandomActiveUserCardNumber(self):
        if len(self.user.active_cards) == 0:
            return None
        return random.choice(self.user.active_cards)

    def getRandomActiveOpponentCardNumber(self, ready=True):
        if len(self.bot.active_cards) == 0:
            return None
        if ready:
            ready_cards = self.getReadyComputerCards()
            if ready_cards:
                return random.choice(ready_cards).card_number
        return random.choice(self.bot.active_cards)

    def increaseUserEnergy(self):
        for card in self.user.cards:
            if card.card_number in self.user.active_cards and card.energy < 1:
                card.energy *= Game.ENERGY_DECREASE_FACTOR / 3
            card.energy = min(max(card.energy, self.MIN_ENERGY), 1)

    def increaseOpponentEnergy(self):
        for card in self.bot.cards:
            if card.energy < 1:
                card.energy *= Game.ENERGY_DECREASE_FACTOR / 3
            card.energy = min(max(card.energy, self.MIN_ENERGY), 1)

    def getReadyComputerCards(self):
        return [
            card for card in self.bot.cards
            if card.energy == 1 and card.card_number in self.bot.active_cards
        ]

    def isReady(self):
        pass


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


def StrategyPvP():
    return StrategyPvPConnector()


class StrategyPvPGame(Strategy):
    def __init__(self, user_id):
        super().__init__()
        self.players[user_id] = Player()

    def isReady(self):
        return len(self.players) == 2

    def getUserCardsInfo(self, user_id):
        return self._getUserCardsInfo(self.players[user_id])

    def attackUser(self, user_card, opponent_card, user_id, opponent_id):
        self.attack(
            self.players[user_id], self.players[opponent_id], user_card, opponent_card)

    def userAttack(self, my_card_num, opponent_card_num):
        strategy = self
        before = strategy.getOpponentCardInfo(opponent_card_num)
        strategy.attackOpponent(my_card_num, opponent_card_num)
        after = strategy.getOpponentCardInfo(opponent_card_num)
        user = strategy.getUserCardInfo(my_card_num)
        return before, after, user
