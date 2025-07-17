import pytest
from app.strategy import StrategyPvPConnector, StrategyPvPGame, StrategyStorage
from app.charcters import Character
from app.base_strategy import Player
from app.storages import MemoryStorage


@pytest.fixture
def storage():
    return MemoryStorage()

@pytest.fixture(autouse=True)
def reset_memory_storage():
    storage = MemoryStorage()
    storage.clear()


def test_strategy_pvp_restore_game(storage):
    game1 = StrategyPvPConnector("1", storage)
    game2 = StrategyPvPConnector("2", storage)
    game2.userAttack("1", 0, 0)
    restored_game = StrategyStorage(storage).get_strategy(game2.uid, StrategyPvPGame)
    assert len(restored_game.players) == 2


def test_strategy_pvp_player_ready(storage):
    StrategyPvPConnector("1", storage)
    game = StrategyPvPConnector("2", storage)
    assert game.isReady()
    assert game.opponents["1"] == "2"
    assert game.opponents["2"] == "1"


def test_strategy_pvp_generate_cards(storage):
    game = StrategyPvPConnector("1", storage)
    game.generateCards()
    player = game.players["1"]
    assert len(player.cards) == game.CARDS_NUMBER
    assert all(isinstance(c, Character) for c in player.cards)


def test_strategy_pvp_attack_flow(storage):
    StrategyPvPConnector("1", storage)
    game = StrategyPvPConnector("2", storage)
    game.generateCards()
    before, after, user = game.userAttack("1", 0, 0)
    assert before["health"] > after["health"]
    assert "energy" in user


def test_strategy_pvp_wait_attack(storage):
    StrategyPvPConnector("1", storage)
    game = StrategyPvPConnector("2", storage)
    game.generateCards()
    health = game.players["2"].cards[0].health
    before, after, user = game.userAttack("1", 0, 0)

    opponent_info, user_info, status = game.waitAttack("2")
    assert user_info["health"] <= health
    assert opponent_info["energy"] <= user['energy']
    assert status in ["turn", "waiting"]


def test_strategy_pvp_victory(storage):
    StrategyPvPConnector("1", storage)
    game = StrategyPvPConnector("2", storage)
    game.generateCards()

    for card in game.players["2"].cards:
        card.health = 0
    game.players["2"].active_cards.clear()

    assert game.getStatus("1") == "Victory!"


def test_strategy_pvp_lose(storage):
    StrategyPvPConnector("1", storage)
    game = StrategyPvPConnector("2", storage)
    game.generateCards()

    for card in game.players["1"].cards:
        card.health = 0
    game.players["1"].active_cards.clear()

    assert game.getStatus("1") == "lose!"


def test_strategy_pvp_turn_order(storage):
    StrategyPvPConnector("1", storage)
    game = StrategyPvPConnector("2", storage)
    game.generateCards()

    assert game.last_turn is None
    game.userAttack("1", 0, 0)
    assert game.last_turn == "1"

    with pytest.raises(Exception):
        game.userAttack("1", 0, 0)

    game.userAttack("2", 0, 0)
    assert game.last_turn == "2"
