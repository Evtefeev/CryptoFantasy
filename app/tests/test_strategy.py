import pytest
from unittest.mock import MagicMock, patch
from strategy import Player, StrategyBot, StrategyPvPConnector, Strategy, pvp_strategies


@pytest.fixture
def mock_card():
    # Create a mock card with the necessary attributes/methods
    card = MagicMock()
    card.health = 100
    card.energy = 0.5
    card.info.return_value = {"health": 100, "energy": 0.5}
    return card


def test_generate_cards_assigns_cards():
    player = Player()
    with patch('strategy.RandomCharacterGenerator.generate_random_character') as mock_gen:
        mock_gen.return_value = MagicMock()
        player.generateCards()
        assert len(player.cards) == Strategy.CARDS_NUMBER
        assert len(player.active_cards) == Strategy.CARDS_NUMBER
        assert all(isinstance(i, int) for i in player.active_cards)


def test_attack_removes_dead_card(mock_card):
    strategy = Strategy()
    attacker = Player()
    defender = Player()

    attacker.cards = [mock_card]
    defender.cards = [mock_card]
    defender.active_cards = [0]

    strategy.game = MagicMock()
    strategy.game.attack = lambda a, d: setattr(d, "health", 0)

    strategy.attack(attacker, defender, 0, 0)
    assert 0 not in defender.active_cards


def test_user_attack_changes_card_info():
    bot = StrategyBot()

    # Mocking the card info methods
    card = MagicMock()
    card.health = 100
    card.energy = 1
    card.info.side_effect = [{"health": 100}, {"health": 0}, {"health": 80}]
    bot.user.cards[0] = card
    bot.bot.cards[0] = card
    bot.bot.active_cards = [0]

    bot.game.attack = lambda a, d: setattr(d, "health", 0)

    before, after, user = bot.userAttack("uid", 0, 0)
    assert before != after
    assert user == {"health": 80}


def test_get_status_victory_or_lose():
    bot = StrategyBot()
    bot.user.active_cards = []
    bot.bot.active_cards = [0]
    assert bot.getStatus("uid") == "lose!"

    bot.user.active_cards = [0]
    bot.bot.active_cards = []
    assert bot.getStatus("uid") == "Victory!"


def test_increase_energy_capped():
    bot = StrategyBot()
    for card in bot.user.cards:
        card.energy = 0.02

    bot.increaseUserEnergy()

    for card in bot.user.cards:
        assert Strategy.MIN_ENERGY <= card.energy <= 1


def test_ready_computer_cards():
    bot = StrategyBot()
    card1 = MagicMock()
    card2 = MagicMock()
    card1.energy = 1
    card2.energy = 0.5
    card1.card_number = 0
    card2.card_number = 1

    bot.bot.cards = [card1, card2]
    bot.bot.active_cards = [0, 1]

    ready_cards = bot.getReadyComputerCards()
    assert len(ready_cards) == 1
    assert ready_cards[0].energy == 1


def test_strategy_pvp_shares_game():
    pvp_strategies.clear()
    game1 = StrategyPvPConnector("1")
    assert len(pvp_strategies) == 1

    game2 = StrategyPvPConnector("2")
    assert isinstance(game2, Strategy)


if __name__ == "__main__":
    pytest.main()
