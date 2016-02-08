# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.
"""

import os
import logging

#redis code
import redis

#gevent code
import gevent

#flask code
from flask import Flask, render_template
from flask_sockets import Sockets

#flask code
app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
sockets = Sockets(app)

#redis code
r = redis.from_url(os.environ['REDISCLOUD_URL'])

#python code
class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = list()
        self.pubsub = r.pubsub()
        self.pubsub.subscribe('chat')
        #redis.set("messageTotal", 1)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

#calls __init__, which creates a list of clients
#sets the pubsub to the redis pubsub, and subscribes to the 'chat' channel
chats = ChatBackend()

#spawns a gevent, using the method run
#run will loop through every message (gotten from pubsub.listen()) to get data
    #loop through every client
        #spawn a gevent using the method send, and arguments client and data

        #send will try to do a client.send(data), but will remove the client
        #if an error occurs
chats.start()

#flask code
@app.route('/')
def hello():
    return render_template('index.html')

#flask code
@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while ws.socket is not None:
        # Sleep to prevent *contstant* context-switches.
        gevent.sleep(0.1)
        #redis.incr("messageTotal")
        message = ws.receive()
        #message.data = message.data + " extra"

        if message:
            app.logger.info(u'Inserting message: {}'.format(message))
            received = r.publish('chat', message)

#flask code
@sockets.route('/receive')
def outbox(ws):
    """Sends (relative to client) outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while ws.socket is not None:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()



