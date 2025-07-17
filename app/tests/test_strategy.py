import pytest
from app.actions import RandomCharacterGenerator
from app.helpers import StrategyStorage
from app.strategy import StrategyBot, StrategyPvP, StrategyPvPConnector, Strategy, StrategyPvPGame
from app.storages import MemoryStorage
from app.base_strategy import Player

@pytest.fixture
def storage():
    return MemoryStorage()

@pytest.fixture(autouse=True)
def reset_memory_storage():
    storage = MemoryStorage()
    storage.clear()


def test_generate_cards_assigns_cards(storage):
    player = Player("test_generate", storage)
    player.generateCards()
    assert len(player.cards) == Strategy.CARDS_NUMBER
    assert len(player.active_cards) == Strategy.CARDS_NUMBER
    assert all(hasattr(card, 'health')
               for card in player.cards)  # Проверяем что это настоящие карты


def test_attack_removes_dead_card(storage):
    strategy = Strategy(storage, users_ids=["attacker", "defender"])
    attacker = strategy.players["attacker"]
    defender = strategy.players["defender"]

    # Генерируем карты с реальными объектами
    attacker.cards = [RandomCharacterGenerator.generate_random_character()]
    defender.cards = [RandomCharacterGenerator.generate_random_character()]
    defender.active_cards = [0]

    # Зануляем здоровье при атаке
    # strategy.game = MagicMock()
    # strategy.game.attack = lambda a, d: setattr(d, "health", 0)
    strategy.CHEAT_MODE = True
    strategy.attack(attacker, defender, 0, 0)
    assert 0 not in defender.active_cards


def test_user_attack_changes_card_info(storage):
    bot = StrategyBot("user", storage)

    card = RandomCharacterGenerator.generate_random_character()
    bot.user.cards[0] = card
    bot.bot.cards[0] = RandomCharacterGenerator.generate_random_character()
    bot.bot.active_cards = [0]

    # bot.game.attack = lambda a, d: setattr(d, "health", 0)

    before, after, user = bot.userAttack("user", 0, 0)
    assert before != after
    assert isinstance(user, dict)
    assert "health" in user


def test_get_status_victory_or_lose(storage):
    bot = StrategyBot('user', storage)
    bot.user.active_cards = []
    bot.bot.active_cards = [0]
    assert bot.getStatus("user") == "lose!"

    bot.user.active_cards = [0]
    bot.bot.active_cards = []
    assert bot.getStatus("user") == "Victory!"


def test_increase_energy_capped(storage):
    bot = StrategyBot('user', storage)
    for card in bot.user.cards:
        card.energy = 0.02

    bot.increaseUserEnergy()

    for card in bot.user.cards:
        assert Strategy.MIN_ENERGY <= card.energy <= 1


def test_ready_computer_cards(storage):
    bot = StrategyBot('user', storage)
    card1 = RandomCharacterGenerator.generate_random_character()
    card2 = RandomCharacterGenerator.generate_random_character()
    card1.energy = 1
    card2.energy = 0.5
    card1.card_number = 0
    card2.card_number = 1

    bot.bot.cards = [card1, card2]
    bot.bot.active_cards = [0, 1]

    ready_cards = bot.getReadyComputerCards()
    assert len(ready_cards) == 1
    assert ready_cards[0].energy == 1


def test_strategy_pvp_shares_game(storage):
    game1 = StrategyPvPConnector("1", storage)
    game2 = StrategyPvPConnector("2", storage)
    assert isinstance(game2, Strategy)
    assert isinstance(game1, Strategy)
    game = StrategyStorage(storage).get_strategy(game1.uid, StrategyPvPGame)
    assert len(game.players) == 2


def test_strategy_to_json(storage):
    game1 = StrategyPvPConnector("1", storage)
    game2 = StrategyPvPConnector("2", storage)
    game = StrategyStorage(storage).get_strategy(game2.uid, StrategyPvPGame)
    assert game.isReady() == True
    game.userAttack('1', 0, 0)
    res = '{"players": ["1", "2"], "last_turn": "1", "opponents": {"1": "2", "2": "1"}, "opponent_card_num": 0, "user_card_num": 0}'
    del game.uid
    assert game.to_json() == res


def test_strategy_from_json(storage):
    game1 = StrategyPvPConnector('1', storage)
    game1 = StrategyPvPConnector('2', storage)
    game1.isReady()
    res = '{"players": ["1", "2"], "last_turn": "1", "opponents": {"1": "2", "2": "1"}, "opponent_card_num": 0, "user_card_num": 0}'
    game1.from_json(res)
    for p in game1.players.values():
        assert isinstance(p, Player)



def test_strategy_pvp_restore_game(storage):
    game1 = StrategyPvPConnector("1", storage)
    game2 = StrategyPvPConnector("2", storage)
    game2.userAttack('1', 0, 0)
    print(game2.uid)
    game: StrategyPvPGame = StrategyStorage(storage).get_strategy(game2.uid, StrategyPvPGame)
    assert len(game.players) == 2

if __name__ == "__main__":
    test_strategy_to_json(MemoryStorage())
