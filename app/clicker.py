import logging
import os
import threading
import time
import uuid
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
from charcters import RandomCharacterGenerator
import actions
from strategy import Strategy, StrategyBot, StrategyPvPConnector
from flask_session import Session
from helpers import *



app = Flask(__name__)

socketio = SocketIO(app)

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