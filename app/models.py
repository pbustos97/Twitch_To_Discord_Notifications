import base64
from datetime import datetime, timedelta
from hashlib import md5
import json
import os
from time import time
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import redis
import rq
from app import db, login
from app.search import add_to_index, remove_from_index, query_index

guildUsers = db.Table('guildUsers',
    db.Column('guildId', db.Integer, db.ForeignKey('guild.guildId')),
    db.Column('userId', db.Integer, db.ForeignKey('user.discordId'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    discordId = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(), index=True)
    email = db.Column(db.String(128), index=True, unique=True)
    avatarURL = db.Column(db.String(256))

    # Guild relationship
    guilds = db.relationship('Guild', secondary=guildUsers, backref='guildId')

    def __repr__(self):
        return "{}: {}".format(self.discordId, self.email)

    def linkGuild(self, guildId):
        self.guilds.append(guildId)

class Guild(db.Model):
    __tablename__ = 'guild'
    
    guildId = db.Column(db.Integer, primary_key=True, unique=True)
    guildName = db.Column(db.String(128))

    # Channel and user relationship
    users = db.relationship('User', secondary=guildUsers, backref='userId')
    channels = db.relationship('Channel', backref='channelId', lazy='dynamic')

    def linkUser(self, discordId):
        self.users.append(discordId)

class Channel(db.Model):
    __tablename__ = 'channel'

    channelId = db.Column(db.Integer, primary_key=True, unique=True)
    channelName = db.Column(db.String(128))
    guildId = db.Column(db.Integer, foreign_key=True, unique=True)

    # Webhook relationship
    webhooks = db.relationship('Webhook', backref='webhookId', lazy='dynamic')

class Webhook(db.Model):
    __tablename__ = 'webhook'

    webhookId = db.Column(db.Integer, primary_key=True, unique=True)
    channelId = db.Column(db.Integer, foreign_key=True, unique=True)

    # Webhook notification relationship
    notifications = db.relationship('Notification', backref='notificationId', lazy='dynamic')

class Notification(db.Model):
    __tablename__ = 'notification'

    notificationId = db.Column(db.String(64), primary_key=True)
    webhookId = db.Column(db.Integer, unique=True, foriegn_key=True)
    twitchId = db.Column(db.Integer, unique=True)