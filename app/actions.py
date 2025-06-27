import random
from charcters import Character, RandomCharacterGenerator


class Game():

    RANDOM_DAMAGE = 0.5
    ENERGY_DECREASE_FACTOR = 20

    def __init__(self) -> None:
        self.hero = RandomCharacterGenerator.generate_random_character()
        self.opponentHero = RandomCharacterGenerator.generate_random_character()
        self.damage_factor = 1

    def respawn(self):
        self.hero = RandomCharacterGenerator.generate_random_character()
        self.opponentHero = RandomCharacterGenerator.generate_random_character()

    def attack(self, attacker: Character, defender: Character) -> float:
        if attacker.health <= 0 or defender.health <= 0:
            return 0
        damage = round(attacker.attack/defender.defense -
                       random.uniform(-self.RANDOM_DAMAGE, self.RANDOM_DAMAGE), 2)
        if isinstance(attacker, defender.counter_class):
            damage *= 2
        damage *= self.damage_factor * attacker.energy
        defender.health -= damage
        attacker.energy /= Game.ENERGY_DECREASE_FACTOR
        return damage

    def attackOpponent(self) -> tuple[float, str, str]:
        if self.hero.health <= 0:
            return (0, "You Died!", "died")
        damage = self.attack(self.hero, self.opponentHero)
        message = ""
        state = "attacked"
        if self.opponentHero.health < 0:
            self.hero.score += 1
            self.levelUp()
            message = f"Opponent {self.opponentHero.name} killed!\n"
            self.opponentHero = RandomCharacterGenerator.generate_random_character()
            message += f"New Opponent is {self.opponentHero.name}!"
            state = "killed"

        return (damage, message, state)

    def attackHero(self) -> tuple[float, str]:
        damage = self.attack(self.opponentHero, self.hero)
        message = ""
        if self.hero.health <= 0:
            message = "You Died!"
        return (damage, message)

    def getState(self):
        return {'hero': self.hero.info(),
                'opponentHero': self.opponentHero.info()}

    def levelUp(self):
        self.hero.base_health += 1
        self.hero.attack += 1
        self.hero.defense += 1
        self.hero.health = self.hero.base_health


class StrategyGame(Game):
    pass
