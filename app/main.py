import logging
import os
import uuid
from flask import Flask, render_template, request, session
import flask
from strategy import Strategy, StrategyBot, StrategyPvP, StrategyPvPConnector, StrategyPvPGame
from flask_session import Session
from helpers import StrategyStorage
import conf

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/clicker')
def clicker():
    return render_template('clicker.html')


@app.route('/strategy')
def strategy():
    return render_template(
        'strategy_menu.html',
        card_ids=range(Strategy.CARDS_NUMBER)
    )


@app.route('/strategy_bot')
def strategy_bot():
    return render_template(
        'strategy.html',
        card_ids=range(Strategy.CARDS_NUMBER)
    )


@app.route('/strategy_pvp')
def strategy_pvp():
    return render_template(
        'strategy_pvp.html',
        card_ids=range(Strategy.CARDS_NUMBER)
    )


strategyStorage = StrategyStorage(conf.STORAGE)


@app.route('/strategy_api', methods=['POST'])
def strategy_api():
    UID = session.get('uid')
    if not UID:
        session['uid'] = str(uuid.uuid4())
        UID = session['uid']

    if request.form.get('action') == 'start':
        mode = request.form.get('game-mode')
        session['game-mode'] = mode
        if mode == "bot":
            strategy = StrategyBot(UID)
        if mode == "pvp":
            strategy = StrategyPvPConnector(flask.session['uid'])
        strategy.generateCards()
        strategy.CHEAT_MODE = conf.ENABLE_CHEAT
        # uid = strategyStorage.save_strategy(strategy)
        session['strategy_id'] = strategy.uid
        return strategy.getUserCardsInfo(flask.session['uid'])
    try:
        type = StrategyBot if session['game-mode'] == "bot" else StrategyPvPGame
    except KeyError:
        return 'Game not started'
        
    strategy: Strategy = strategyStorage.get_strategy(session['strategy_id'], type)
    if not strategy:
        return 'Game not started'

    if request.form.get('action') == 'my_cards':
        return strategy.getUserCardsInfo(UID)

    if request.form.get('action') == 'attack':
        my_card_num = int(request.form.get('my_card_num'))
        opponent_card_num = int(request.form.get('opponent_card_num'))
        try:
            before, after, user = strategy.userAttack(
                UID, my_card_num, opponent_card_num)
            return {
                "status": "ok",
                "before": before,
                "after": after,
                "user": user
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }, 400

    if request.form.get('action') == 'wait_for_opponent_turn':
        status = strategy.getStatus(UID)
        if status:
            return {'status': status}
        opponent_info, user_info, status = strategy.waitAttack(UID)
        return {'status': status, 'opponent_info': opponent_info, 'user_info': user_info}

    if request.form.get('action') == 'wait_for_opponent':
        if strategy.isReady():
            return {'status': 'connected', 'turn': strategy.getTurn(UID)}
        return {'stauts': 'waiting'}

    return "invalid action"


if __name__ == '__main__':
    app.run(port=8888, debug=True)
