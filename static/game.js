const socket = io()

let log = ""

let hero_text = "Ваш герой:"
let health_text = "Здоровье:"
let attack_text = "Атака:"
let defence_text = "Атака:"
let score_text = "Опыт:"
let enemi_text="Вражеский герой:"

// let hero_text = "Ваш герой:"
// let health_text = "❤️"
// let attack_text = "⚡"
// let defence_text = "🛡️"
// let score_text = "Опыт:"
// let enemi_text="Вражеский герой:"

socket.on('gameState', (state) => {
    document.getElementById('hero-name').innerText = `${hero_text} ${state.hero.name}`
    document.getElementById('hero').style.backgroundImage = `url('/static/imgs/${state.hero.image}')`
    document.getElementById('hero-health').innerText = `${health_text} ${state.hero.health}`
    document.getElementById('hero-attack').innerText = `${attack_text} ${state.hero.attack}`
    document.getElementById('hero-defense').innerText = `${defence_text} ${state.hero.defense}`
    document.getElementById('hero-score').innerText = `${score_text} ${state.hero.score}`
    document.getElementById('opponent-hero-name').innerText = `${enemi_text} ${state.opponentHero.name}`
    document.getElementById('opponent-hero').style.backgroundImage = `url('/static/imgs/${state.opponentHero.image}')`
    document.getElementById('opponent-hero-health').innerText = `${health_text} ${state.opponentHero.health}`
    document.getElementById('opponent-hero-attack').innerText = `${attack_text} ${state.opponentHero.attack}`
    document.getElementById('opponent-hero-defense').innerText = `${defence_text} ${state.opponentHero.defense}`
    if (state.hero.health <= 0) {

        document.getElementById("arena").style.backgroundColor = "gray";
    } else {

        document.getElementById("arena").style.backgroundColor = "";
    }


})

socket.on('heroAttackDamage', (damage, message) => {
    log += 'Атакуем противника -' + damage + 'XP\n'
    log += message ? message + '\n\n' : ''
    if (message.includes("killed")) {
        fight(false);
    }
    document.getElementById('log').innerText = log + "\n\n\n\n"
})

socket.on('opponentAttackDamage', (damage, message) => {
    log += 'Противник атакует -' + damage + 'XP\n'
    log += message ? message + '\n\n' : ''
    document.getElementById('log').innerText = log + "\n\n\n\n"
})

const playCard = (card = 'none') => {
    socket.emit('playCard', card)
    console.log('attack')
    updateScroll();
}

const fight = (start = true) => {
    if (start) {
        document.getElementById('fog').style.display = "none"

    } else {
        document.getElementById('fog').style.display = "flex"

    }
}

document.getElementById('fight').onclick = fight;

const respawnPlayer = () => {
    socket.emit('respawn')
    console.log('resapwn')
}

const hand = document.getElementById('opponent-hero')
hand.onclick = playCard


const respawn = document.getElementById('respawn')
respawn.onclick = respawnPlayer


var scrolled = false
function updateScroll() {
    if (!scrolled) {
        var element = document.getElementById('log')
        element.scrollTop = element.scrollHeight
    }
}