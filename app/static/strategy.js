let time_scale = 0.5


// let hero_text = "Ваш герой:"
// let health_text = "Здоровье:"
// let attack_text = "Атака:"
// let defence_text = "Атака:"
// let score_text = "Опыт:"
// let enemi_text="Вражеский герой:"

let hero_text = "Ваш герой:"
let health_text = "❤️"
let energy_text = "⚡"
let attack_text = "🗡️"
let defence_text = "🛡️"
let score_text = "Опыт:"
let enemi_text = "Вражеский герой:"



let you_turn = false;
let waitInterval;
let turnInterval;
let game_mode;


function startGame(mode) {
    $.post("strategy_api", { action: "start", "game-mode": mode }, (result) => {
        console.log(result);
        let id = 0;
        result.forEach((state) => {
            let card = $('#card_' + id);
            fillCard(state, card);
            id++;
        });
    });
}




function loadMyCards() {
    $.post("strategy_api", { action: "my_cards" }, (result) => {
        console.log(result);
        let id = 0;
        result.forEach((state) => {
            let card = $('#card_' + id);
            fillCard(state, card);
            id++;
        });
    });
}


function fillOponentCard(card_data) {
    if (card_data) {
        console.log(card_data);
        let id = card_data.card_number;
        let card = $('#opponent_card_' + id);
        $(".opponent_card").css({ border: "1px solid #000" })
        card.css({ border: "2px solid #f00" })
        fillCard(card_data, card);
    }
}

function fillUserCard(card_data) {
    console.log(card_data);
    let id = card_data.card_number;
    let card = $('#card_' + id);
    $(".user_card").css({ border: "1px solid #000" })
    card.css({ border: "2px solid #f00" })
    fillCard(card_data, card);
}

function fillCard(card_data, card) {

    card.find('#hero-name')[0].innerText = `${card_data.name}`
    card[0].style.backgroundImage = `url('/static/imgs/${card_data.image}')`
    card.find('#hero-health')[0].innerText = `${health_text} ${card_data.health}`
    card.find('#hero-attack')[0].innerText = `${attack_text} ${card_data.attack}`
    card.find('#hero-defense')[0].innerText = `${defence_text} ${card_data.defense}`
    if (card.find('#hero-energy').length > 0)
        card.find('#hero-energy')[0].innerText = `${energy_text} ${card_data.energy}`
    const healthBar = card.find('#health-bar')[0];

    if (card_data.health <= 0) {
        card[0].classList.add('gray-foreground');
        healthPercentage = 0;
    }

    const heroEnergyBar = card.find('#hero-energy-bar')[0];

    updateHeroBar(healthBar, card_data.health, card_data.base_health);
    updateHeroBar(heroEnergyBar, card_data.energy, 1);

}

function updateHeroBar(bar, value, max) {
    let healthPercentage = (value / max) * 100;
    if (bar)
        bar.style.width = healthPercentage + '%';
}

function waitForOpponentTurn() {
    you_turn = false;
    setOpponentStatus("Waiting for opponent turn");
    $.post("strategy_api", { action: "wait_for_opponent_turn" }, (result) => {
        console.log(result);
        if (result.status == "waiting") {
            return
        }
        if (result.status == "turn") {
            clearInterval(turnInterval);
            you_turn = true;
            let opponent_card = result.opponent_info
            fillOponentCard(opponent_card)
            setTimeout(fillUserCard.bind(null, result.user_info), 2000 * time_scale)
            setTimeout(loadMyCards, 2500 * time_scale)
            setOpponentStatus("You turn!");
            return;
        }
        setOpponentStatus(result.status);
        clearInterval(turnInterval);
        alert(result.status);
    });
}


function setOpponentStatus(status_text) {
    $("#player_info_game").text(status_text);
}



function waitForOpponent() {
    $.post("strategy_api", { action: "wait_for_opponent" }, (result) => {
        console.log(result);
        setOpponentStatus("Waiting for opponent...");
        if (result.status === "connected") {
            clearInterval(waitInterval);
            setOpponentStatus("Connected to opponent");
            $("#opponent_cards").css({ display: "flex" });
            if (!result.turn) {
                clearInterval(turnInterval);
                turnInterval = setInterval(waitForOpponentTurn, 1000);
            } else {
                setOpponentStatus("You turn!");
                you_turn = true;
            }
        }

    });
}

function attack(my_card, opponent_card) {
    if (you_turn) {
        $.post("strategy_api", {
            action: "attack",
            my_card_num: my_card,
            opponent_card_num: opponent_card
        }, (result) => {
            let card_data = result.before
            console.log(result.after);
            fillUserCard(result.user);
            fillOponentCard(card_data);
            setTimeout(fillOponentCard.bind(null, result.after), 2000 * time_scale)
            // setTimeout(waitForOpponentTurn, 5000 * time_scale)
            clearInterval(turnInterval);
            if (game_mode == "pvp") {
                turnInterval = setInterval(waitForOpponentTurn, 1000);
            } else if (game_mode == "bot") {
                waitForOpponentTurn()
            }

        });
    } else {
        alert("Waiting opponent turn");
    }

}

let my_card_num = -1

$(".opponent_card").on("click", function () {
    let opponent_card_num = parseInt($(this).attr('id').match(/(\d+)$/)[0], 10)
    $(".opponent_card").css({ border: "1px solid #000" })
    $(this).css({ border: "2px solid #f00" })
    if (my_card_num != -1) {
        attack(my_card_num, opponent_card_num);
        console.log(my_card_num, opponent_card_num);
    }
});


$(".user_card").on("click", function () {
    my_card_num = parseInt($(this).attr('id').match(/(\d+)$/)[0], 10)
    $(".user_card").css({ border: "1px solid #000" })
    $(this).css({ border: "2px solid #0f0" })
});


function startBot() {
    game_mode = "bot";

    startGame("bot");
    you_turn = true;
}

function startPVP() {
    game_mode = "pvp";
    $("#opponent_cards").css({ display: "none" });
    startGame("pvp");
    waitInterval = setInterval(waitForOpponent, 1000);


}


