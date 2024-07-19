import random
from charcters import Character, RandomCharacterGenerator


class Game():

    RANDOM_DAMAGE = 0.5

    def __init__(self) -> None:
        self.hero = RandomCharacterGenerator.generate_random_character()
        self.opponentHero = RandomCharacterGenerator.generate_random_character()

    def respawn(self):
        self.hero = RandomCharacterGenerator.generate_random_character()
        self.opponentHero = RandomCharacterGenerator.generate_random_character()

    def attack(self, attacker: Character, defender: Character) -> float:
        if attacker.health <= 0:
            return 0
        damage = round(attacker.attack/defender.defense -
                       random.uniform(-self.RANDOM_DAMAGE, self.RANDOM_DAMAGE), 2)
        defender.health -= damage
        return damage

    def attackOpponent(self) -> tuple[float, str]:
        damage = self.attack(self.hero, self.opponentHero)
        message = ""
        if self.opponentHero.health < 0:
            self.hero.score += 1
            message = f"Opponent {self.opponentHero.name} killed!\n"
            self.opponentHero = RandomCharacterGenerator.generate_random_character()
            message += f"New Opponent is {self.opponentHero.name}!"

        return (damage, message)

    def attackHero(self) -> tuple[float, str]:
        damage = self.attack(self.opponentHero, self.hero)
        message = ""
        if self.hero.health <= 0:
            message = "You Died!"
        return (damage, message)

    def getState(self):
        return {'hero': self.hero.info(),
                'opponentHero': self.opponentHero.info()}
