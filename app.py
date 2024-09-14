import os
import threading
import time
import uuid
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
from charcters import RandomCharacterGenerator
import actions
from strategy import Strategy
from flask_session import Session

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

socketio = SocketIO(app)

clients = {}

strategies = {}


def get_session_info():
    return clients[request.sid]


def get_startegy() -> Strategy | None:

    if session.get('strategy_id') in strategies.keys():
        return strategies[session.get('strategy_id')]
    else:
        return None


def save_strategy(strategy):
    uid = uuid.uuid4()
    strategies[uid] = strategy
    session['strategy_id'] = uid


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/clicker')
def clicker():
    return render_template('clicker.html')


@app.route('/strategy')
def strategy():
    return render_template(
        'strategy.html',
        card_ids=range(Strategy.CARDS_NUMBER)
    )


@app.route('/strategy_api', methods=['POST'])
def strategy_api():

    if request.form.get('action') == 'start':
        strategy = Strategy()
        strategy.generateCards()
        save_strategy(strategy)
        return strategy.getUserCardsInfo()

    strategy: Strategy = get_startegy()
    if not strategy:
        return 'Game not started'

    if request.form.get('action') == 'my_cards':

        return strategy.getUserCardsInfo()

    if request.form.get('action') == 'attack':
        my_card_num = int(request.form.get('my_card_num'))
        opponent_card_num = int(request.form.get('opponent_card_num'))
        before = strategy.getOpponentCardInfo(opponent_card_num)
        strategy.attackOpponent(my_card_num, opponent_card_num)
        after = strategy.getOpponentCardInfo(opponent_card_num)
        user = strategy.getUserCardInfo(my_card_num)
        return {'before': before, 'after': after, 'user': user}


    if request.form.get('action') == 'wait_for_opponent':
        opponent_card_num = strategy.getRandomActiveOpponentCardNumber()
        if opponent_card_num == None:
            return {'status': 'Victory!'}
        user_card_num = strategy.getRandomActiveUserCardNumber()
        if user_card_num == None:
            return {'status': 'lose!'}
        strategy.attackUser(user_card_num, opponent_card_num)
        user_card_num = strategy.getRandomActiveUserCardNumber()
        user_info = strategy.getUserCardInfo(user_card_num)
        
        if user_card_num == None:
            return {'status': 'lose!', 'user_info': user_info}
        opponent_info = strategy.getOpponentCardInfo(opponent_card_num)
        return {'opponent_info': opponent_info, 'user_info': user_info}

    return "invalid action"


@socketio.on('connect')
def handle_connect():
    cid = request.sid
    print("Connected:", cid)
    clients[cid] = (cid, actions.Game(), threading.Lock())
    id, game, game_state_lock = get_session_info()
    with game_state_lock:
        emit('gameState', game.getState())


@socketio.on('respawn')
def handle_connect():
    cid, game, game_state_lock = get_session_info()

    with game_state_lock:
        game.respawn()
        emit('gameState', game.getState(), to=cid)


@socketio.on('playCard')
def handle_play_card(card):
    cid, game, game_state_lock = get_session_info()

    with game_state_lock:
        damage, message, state = game.attackOpponent()
        emit('heroAttackDamage', (damage, message), to=cid)
        emit('gameState', game.getState(), to=cid)

        if damage == 0 or state == "killed":
            return

        em_id = id(game.opponentHero)
    time.sleep(1)
    with game_state_lock:
        if em_id == id(game.opponentHero):
            damage, message = game.attackHero()
            if damage > 0:
                emit('opponentAttackDamage', (damage, message), to=cid)
                emit('gameState', game.getState(), to=cid)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)
