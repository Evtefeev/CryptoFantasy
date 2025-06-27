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
