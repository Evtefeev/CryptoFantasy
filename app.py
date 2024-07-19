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


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    emit('gameState', game.getState())

@socketio.on('respawn')
def handle_connect():
    game.respawn()
    emit('gameState', game.getState())

@socketio.on('playCard')
def handle_play_card(card):
    damage, message = game.attackOpponent()
    emit('heroAttackDamage', (damage, message), broadcast=True)
    emit('gameState', game.getState(), broadcast=True)
    time.sleep(1)
    damage, message = game.attackHero()
    if damage > 0:
        emit('opponentAttackDamage', (damage, message), broadcast=True)
        emit('gameState', game.getState(), broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
