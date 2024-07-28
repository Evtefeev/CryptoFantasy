from actions import RandomCharacterGenerator


class Strategy:

    CARDS_NUMBER = 6

    def generateCards():
        return [RandomCharacterGenerator.generate_random_character().info() for _ in range(Strategy.CARDS_NUMBER+1)]
