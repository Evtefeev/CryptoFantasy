import pytest
from unittest.mock import MagicMock

from strategy import Player, StrategyPvPGame

# Assuming you import like this:
# from strategy_game import StrategyPvPGame, Player, StrategyGame, Game

class DummyCard:
    def __init__(self):
        self.health = 100
        self.energy = 0.1
        self.card_number = None

    def info(self):
        return {"health": self.health, "energy": self.energy}

    def set_card_number(self, num):
        self.card_number = num

class DummyGame:
    ENERGY_DECREASE_FACTOR = 0.9

    def __init__(self):
        self.damage_factor = 10

    def attack(self, attacker, defender):
        defender.health -= 20  # example attack

@pytest.fixture
def monkey_patch_game(monkeypatch):
    monkeypatch.setattr("strategy.RandomCharacterGenerator.generate_random_character", lambda: DummyCard())
    monkeypatch.setattr("strategy.StrategyGame", DummyGame)
    monkeypatch.setattr("strategy.Game", DummyGame)


def test_game_initialization(monkey_patch_game):
    game = StrategyPvPGame("user1")
    assert "user1" in game.players
    assert isinstance(game.players["user1"], Player)


def test_player_ready(monkey_patch_game):
    game = StrategyPvPGame("user1")
    game.players["user2"] = Player()
    ready = game.isReady()
    assert ready is True
    assert game.opponents["user1"] == "user2"
    assert game.opponents["user2"] == "user1"


def test_card_generation(monkey_patch_game):
    game = StrategyPvPGame("user1")
    game.players["user1"].generateCards()
    assert len(game.players["user1"].cards) == game.CARDS_NUMBER
    assert all(isinstance(c, DummyCard) for c in game.players["user1"].cards)


def test_attack_flow(monkey_patch_game):
    game = StrategyPvPGame("user1")
    game.players["user2"] = Player()
    game.isReady()
    game.generateCards()

    uid, opponent_id = "user1", "user2"
    user_card = 0
    opponent_card = 0
    before, after, user = game.userAttack(uid, user_card, opponent_card)

    assert before["health"] == 100
    assert after["health"] == 80  # Assuming 20 damage
    assert "energy" in user


def test_wait_attack(monkey_patch_game):
    game = StrategyPvPGame("user1")
    game.players["user2"] = Player()
    game.isReady()
    game.generateCards()
    game.userAttack("user1", 0, 0)

    opponent_info, user_info, status = game.waitAttack("user2")
    assert opponent_info["health"] <= 100
    assert user_info["health"] <= 100
    assert status in ["turn", "waiting"]


def test_victory_condition(monkey_patch_game):
    game = StrategyPvPGame("user1")
    game.players["user2"] = Player()
    game.isReady()
    game.generateCards()
    # Kill all opponent cards
    for card in game.players["user2"].cards:
        card.health = 0
    game.players["user2"].active_cards.clear()

    status = game.getStatus("user1")
    assert status == "Victory!"


def test_lose_condition(monkey_patch_game):
    game = StrategyPvPGame("user1")
    game.players["user2"] = Player()
    game.isReady()
    game.generateCards()
    # Kill all user cards
    for card in game.players["user1"].cards:
        card.health = 0
    game.players["user1"].active_cards.clear()

    status = game.getStatus("user1")
    assert status == "lose!"

