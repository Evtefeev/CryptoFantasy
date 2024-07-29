let time_scale = 0.5



$.post("strategy_api", { action: "start" }, (result) => {
    console.log(result);
    let id = 0;
    result.forEach((state) => {
        let card = $('#card_' + id);
        console.log(state);
        card.find('#hero-name')[0].innerText = `${state.name}`
        card.find('#hero')[0].style.backgroundImage = `url('/static/imgs/${state.image}')`
        card.find('#hero-health')[0].innerText = `Здоровье: ${state.health}`
        card.find('#hero-attack')[0].innerText = `Атака: ${state.attack}`
        card.find('#hero-defense')[0].innerText = `Броня: ${state.defense}`
        card.find('#hero-score')[0].innerText = `Опыт: ${state.score}`
        id++;
    });
});

function fillOponentCard(card_data) {
    console.log(card_data);
    let id = card_data.card_number;

    let card = $('#opponent_card_' + id);


    $(".opponent_card").css({ border: "1px solid #000" })
    card.css({ border: "2px solid #f00" })
    fillCard(card_data, card);
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
    card.find('#hero')[0].style.backgroundImage = `url('/static/imgs/${card_data.image}')`
    card.find('#hero-health')[0].innerText = `Здоровье: ${card_data.health}`
    card.find('#hero-attack')[0].innerText = `Атака: ${card_data.attack}`
    card.find('#hero-defense')[0].innerText = `Броня: ${card_data.defense}`
    card.find('#hero-score')[0].innerText = `Опыт: ${card_data.score}`
    const healthBar = card.find('#health-bar')[0];

    // Calculate the width of the health bar as a percentage
    let healthPercentage = (card_data.health / card_data.base_health) * 100;



    if (card_data.health <= 0) {
        card[0].classList.add('gray-foreground');
        healthPercentage = 0;
    }
    // Update the health bar width and the displayed health value
    healthBar.style.width = healthPercentage + '%';
}


function waitForOpponent() {
    $.post("strategy_api", { action: "wait_for_opponent" }, (result) => {
        console.log(result);
        if (result.status) {
            alert(result.status);
            return;
        }
        let opponent_card = result.opponent_info
        fillOponentCard(opponent_card)
        setTimeout(fillUserCard.bind(null, result.user_info), 2000*time_scale)

    });
}

function attack(my_card, opponent_card) {
    $.post("strategy_api", {
        action: "attack",
        my_card_num: my_card,
        opponent_card_num: opponent_card
    }, (result) => {
        let card_data = result.before
        console.log(result.after);
        fillOponentCard(card_data);

        setTimeout(fillOponentCard.bind(null, result.after), 2000*time_scale)
        setTimeout(waitForOpponent, 5000*time_scale)

    });
}

let my_card_num = 0

$(".opponent_card").on("click", function () {
    let opponent_card_num = parseInt($(this).attr('id').match(/(\d+)$/)[0], 10)
    $(".opponent_card").css({ border: "1px solid #000" })
    $(this).css({ border: "2px solid #f00" })
    attack(my_card_num, opponent_card_num);
});


$(".user_card").on("click", function () {
    my_card_num = parseInt($(this).attr('id').match(/(\d+)$/)[0], 10)
    $(".user_card").css({ border: "1px solid #000" })
    $(this).css({ border: "2px solid #0f0" })
});