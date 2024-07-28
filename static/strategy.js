$.post("strategy_api", { action: "my_cards" }, (result) => {
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