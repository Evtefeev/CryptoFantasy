import random


class Character:
    def __init__(self, name: str, health: int, attack: int, defense: int, counter_class):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.counter_class = counter_class
        self.image = name.replace(" ", "_")+".png"
        self.score = 0

    def __repr__(self):
        return f"{self.name} (Health: {self.health}, Attack: {self.attack}, Defense: {self.defense})"

    def take_damage(self, damage):
        self.health -= damage
        return self.health > 0

    def info(self):
        return {
            'name': self.name,
            'health': round(self.health, 2),
            'attack': self.attack,
            'defense': self.defense,
            'score': self.score,
            'image': self.image
        }


class Human(Character):
    pass


class Elf(Character):
    pass


class Orc(Character):
    pass


class Undead(Character):
    pass


# Люди
class Knight(Human):
    def __init__(self):
        super().__init__("Knight", 100, 15, 10, Mage)


class Archer(Human):
    def __init__(self):
        super().__init__("Archer", 80, 10, 5, Rogue)


class Mage(Human):
    def __init__(self):
        super().__init__("Mage", 60, 20, 5, Rogue)


class Paladin(Human):
    def __init__(self):
        super().__init__("Paladin", 120, 12, 15, Necromancer)


class Rogue(Human):
    def __init__(self):
        super().__init__("Rogue", 70, 18, 8, Knight)


class Priest(Human):
    def __init__(self):
        super().__init__("Priest", 60, 10, 5, Archer)


# Эльфы
class ForestGuard(Elf):
    def __init__(self):
        super().__init__("Forest Guard", 90, 14, 8, ElfShaman)


class Assassin(Elf):
    def __init__(self):
        super().__init__("Assassin", 70, 20, 7, Warrior)


class Sorcerer(Elf):
    def __init__(self):
        super().__init__("Sorcerer", 60, 22, 4, Knight)


class Druid(Elf):
    def __init__(self):
        super().__init__("Druid", 80, 10, 12, Warrior)


class ElfArcher(Elf):
    def __init__(self):
        super().__init__("Elf Archer", 75, 12, 6, Assassin)


class ElfShaman(Elf):
    def __init__(self):
        super().__init__("Elf Shaman", 65, 15, 7, Sorcerer)


# Орки
class Berserk(Orc):
    def __init__(self):
        super().__init__("Berserk", 110, 18, 6, Warlock)


class Hunter(Orc):
    def __init__(self):
        super().__init__("Hunter", 85, 12, 8, ElfShaman)


class OrcShaman(Orc):
    def __init__(self):
        super().__init__("Orc Shaman", 70, 15, 7, Warrior)


class Chief(Orc):
    def __init__(self):
        super().__init__("Chief", 100, 14, 10, Assassin)


class Warlock(Orc):
    def __init__(self):
        super().__init__("Warlock", 60, 20, 5, Hunter)


class Warrior(Orc):
    def __init__(self):
        super().__init__("Warrior", 95, 16, 12, Berserk)


# Нежить
class Lich(Undead):
    def __init__(self):
        super().__init__("Lich", 80, 22, 5, Paladin)


class Vampire(Undead):
    def __init__(self):
        super().__init__("Vampire", 75, 18, 7, Priest)


class Necromancer(Undead):
    def __init__(self):
        super().__init__("Necromancer", 65, 20, 5, Mage)


class Ghost(Undead):
    def __init__(self):
        super().__init__("Ghost", 70, 15, 10, Archer)


class SkeletonWarrior(Undead):
    def __init__(self):
        super().__init__("Skeleton Warrior", 85, 12, 8, ForestGuard)


class Zombie(Undead):
    def __init__(self):
        super().__init__("Zombie", 90, 10, 10, Druid)


class CharacterFactory:
    @staticmethod
    def create_character(race, character_type) -> Character:
        if race == "Human":
            if character_type == "Knight":
                return Knight()
            elif character_type == "Archer":
                return Archer()
            elif character_type == "Mage":
                return Mage()
            elif character_type == "Paladin":
                return Paladin()
            elif character_type == "Rogue":
                return Rogue()
            elif character_type == "Priest":
                return Priest()
        elif race == "Elf":
            if character_type == "ForestGuard":
                return ForestGuard()
            elif character_type == "Assassin":
                return Assassin()
            elif character_type == "Sorcerer":
                return Sorcerer()
            elif character_type == "Druid":
                return Druid()
            elif character_type == "ElfArcher":
                return ElfArcher()
            elif character_type == "ElfShaman":
                return ElfShaman()
        elif race == "Orc":
            if character_type == "Berserk":
                return Berserk()
            elif character_type == "Hunter":
                return Hunter()
            elif character_type == "OrcShaman":
                return OrcShaman()
            elif character_type == "Chief":
                return Chief()
            elif character_type == "Warlock":
                return Warlock()
            elif character_type == "Warrior":
                return Warrior()
        elif race == "Undead":
            if character_type == "Lich":
                return Lich()
            elif character_type == "Vampire":
                return Vampire()
            elif character_type == "Necromancer":
                return Necromancer()
            elif character_type == "Ghost":
                return Ghost()
            elif character_type == "SkeletonWarrior":
                return SkeletonWarrior()
            elif character_type == "Zombie":
                return Zombie()
        return None


class RandomCharacterGenerator:
    races = ["Human", "Elf", "Orc", "Undead"]
    human_classes = ["Knight", "Archer", "Mage", "Paladin", "Rogue", "Priest"]
    elf_classes = ["ForestGuard", "Assassin",
                   "Sorcerer", "Druid", "ElfArcher", "ElfShaman"]
    orc_classes = ["Berserk", "Hunter",
                   "OrcShaman", "Chief", "Warlock", "Warrior"]
    undead_classes = ["Lich", "Vampire", "Necromancer",
                      "Ghost", "SkeletonWarrior", "Zombie"]

    @staticmethod
    def generate_random_character() -> Character:
        race = random.choice(RandomCharacterGenerator.races)
        if race == "Human":
            character_type = random.choice(
                RandomCharacterGenerator.human_classes)
        elif race == "Elf":
            character_type = random.choice(
                RandomCharacterGenerator.elf_classes)
        elif race == "Orc":
            character_type = random.choice(
                RandomCharacterGenerator.orc_classes)
        elif race == "Undead":
            character_type = random.choice(
                RandomCharacterGenerator.undead_classes)
        return CharacterFactory.create_character(race, character_type)


if __name__ == "__main__":

    # Пример использования генератора случайных персонажей
    random_character = RandomCharacterGenerator.generate_random_character()
    print(random_character)
    print(vars(random_character))

# # Пример использования фабрики
# factory = CharacterFactory()

# knight = factory.create_character("Human", "Knight")
# archer = factory.create_character("Human", "Archer")
# mage = factory.create_character("Human", "Mage")

# forest_guard = factory.create_character("Elf", "ForestGuard")
# assassin = factory.create_character("Elf", "Assassin")
# sorcerer = factory.create_character("Elf", "Sorcerer")

# berserk = factory.create_character("Orc", "Berserk")
# hunter = factory.create_character("Orc", "Hunter")
# orc_shaman = factory.create_character("Orc", "OrcShaman")

# lich = factory.create_character("Undead", "Lich")
# vampire = factory.create_character("Undead", "Vampire")
# necromancer = factory.create_character("Undead", "Necromancer")

# print(knight)
# print(archer)
# print(mage)
# print(forest_guard)
# print(assassin)
# print(sorcerer)
# print(berserk)
# print(hunter)
# print(orc_shaman)
# print(lich)
# print(vampire)
# print(necromancer)
