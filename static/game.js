const socket = io()

let log = ""


socket.on('gameState', (state) => {
    document.getElementById('hero-name').innerText = `Ваш герой: ${state.hero.name}`
    document.getElementById('hero').style.backgroundImage = `url('/static/imgs/${state.hero.image}')`
    document.getElementById('hero-health').innerText = `Здоровье: ${state.hero.health}`
    document.getElementById('hero-attack').innerText = `Атака: ${state.hero.attack}`
    document.getElementById('hero-defense').innerText = `Броня: ${state.hero.defense}`
    document.getElementById('hero-score').innerText = `Опыт: ${state.hero.score}`
    document.getElementById('opponent-hero-name').innerText = `Вражеский герой: ${state.opponentHero.name}`
    document.getElementById('opponent-hero').style.backgroundImage = `url('/static/imgs/${state.opponentHero.image}')`
    document.getElementById('opponent-hero-health').innerText = `Здоровье: ${state.opponentHero.health}`
    document.getElementById('opponent-hero-attack').innerText = `Атака: ${state.opponentHero.attack}`
    document.getElementById('opponent-hero-defense').innerText = `Броня: ${state.opponentHero.defense}`
    if (state.hero.health <= 0) {
        document.getElementById("attack").disabled = true;
        document.getElementById("arena").style.backgroundColor = "gray";
    } else {
        document.getElementById("attack").disabled = false;
        document.getElementById("arena").style.backgroundColor = "";
    }


})

socket.on('heroAttackDamage', (damage, message) => {
    log += 'Атакуем противника -' + damage + 'XP\n'
    log += message ? message + '\n\n' : ''
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


const respawnPlayer = () => {
    socket.emit('respawn')
    console.log('resapwn')
}

const hand = document.getElementById('hand').getElementsByTagName('button')[0]
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