import random
from actions import RandomCharacterGenerator, StrategyGame


class Strategy:

    CARDS_NUMBER = 6

    def __init__(self) -> None:
        self.user_cards = []
        self.computer_cards = []
        self.game = StrategyGame()
        self.game.damage_factor = 10
        self.active_user_cards = []
        self.active_computer_cards = []

    def generateCards(self):
        self.user_cards = self.__genetrateCards()
        self.computer_cards = self.__genetrateCards()
        self.__generateCardsNumbers()

    def getUserCards(self):
        return self.user_cards

    def getUserCardsInfo(self):
        return [card.info() for card in self.user_cards]

    def __genetrateCards(self):
        return [RandomCharacterGenerator.generate_random_character() for _ in range(Strategy.CARDS_NUMBER)]

    def __generateCardsNumbers(self):
        for n, card in enumerate(self.computer_cards):
            card.set_card_number(n)
            self.active_computer_cards.append(n)
            
        for n, card in enumerate(self.user_cards):
            card.set_card_number(n)
            self.active_user_cards.append(n)

    def getOpponentCardInfo(self, num):
        return self.computer_cards[num].info()
    
    def getUserCardInfo(self, num):
        return self.user_cards[num].info()

    def attackOpponent(self, user_card, opponent_card):
        self.game.attack(
            self.user_cards[user_card], self.computer_cards[opponent_card])
        if self.computer_cards[opponent_card].health <= 0:
            self.active_computer_cards.remove(opponent_card)


    def attackUser(self, user_card, opponent_card):
        self.game.attack(
            self.computer_cards[opponent_card],self.user_cards[user_card])
        if self.user_cards[user_card].health <= 0:
            self.active_user_cards.remove(user_card)
    
    def getRandomActiveOpponentCardNumber(self):
        if len(self.active_computer_cards) == 0:
            return None
        return random.choice(self.active_computer_cards)
    
    def getRandomActiveUserCardNumber(self):
        if len(self.active_user_cards) == 0:
            return None
        return random.choice(self.active_user_cards)
        