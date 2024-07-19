import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from charcters import RandomCharacterGenerator
import actions

app = Flask(__name__)
socketio = SocketIO(app)

hero = RandomCharacterGenerator.generate_random_character()
opponentHero = RandomCharacterGenerator.generate_random_character()




game = actions.Game()

# Lock for thread-safe game state updates
game_state_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    with game_state_lock:
        emit('gameState', game.getState())

@socketio.on('respawn')
def handle_connect():
    with game_state_lock:
        game.respawn()
        emit('gameState', game.getState())

@socketio.on('playCard')
def handle_play_card(card):
    with game_state_lock:
        damage, message, state = game.attackOpponent()
        emit('heroAttackDamage', (damage, message), broadcast=True)
        emit('gameState', game.getState(), broadcast=True)
        
        if damage == 0 or state == "killed":
            return
            
        em_id = id(game.opponentHero)
    time.sleep(1)
    with game_state_lock:
        if em_id == id(game.opponentHero):
            damage, message = game.attackHero()
            if damage > 0:
                emit('opponentAttackDamage', (damage, message), broadcast=True)
                emit('gameState', game.getState(), broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
