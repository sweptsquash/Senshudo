#!/usr/bin/env python

import os
import mysql.connector
import schedule
import time
import datetime
from configparser import ConfigParser
from twitch import TwitchClient
from twitch.constants import STREAM_TYPES, STREAM_TYPE_LIVE
from twitch.api.base import TwitchAPI
from SenServiceCore import SenServiceCore

client = None
config = None
mydb = None

def SenshudoOAuth():
    global client, config, mydb

    currect_dir = os.path.dirname(os.path.realpath(__file__))

    print('Running Crawler...')

    if currect_dir.find('config.cfg'):
        config = ConfigParser()
        config.read(os.path.join(currect_dir, 'config.cfg'))

        if 'Credentials' in config.sections():
            # Twitch OAuth
            client = TwitchClient(
                client_id=config['Credentials'].get('client_id'), 
                oauth_token=config['Credentials'].get('oauth_token')
            )

            # Senshudo OAuth Check
            SenCore = SenServiceCore(
                client_id=config['Credentials'].get('client_id'), 
                oauth_token=config['Credentials'].get('oauth_token'),
                client_secret=config['Credentials'].get('client_secret')
            )

            if mydb is None:
                mydb = mysql.connector.connect(
                    host=config['Credentials'].get('db_host'),
                    user=config['Credentials'].get('db_username'),
                    passwd=config['Credentials'].get('db_password'),
                    database=config['Credentials'].get('db_database')
                )

            # Ensure OAuth Token is updated
            config.set('Credentials', 'oauth_token', SenCore._checkToken())

            # Save Config.cfg Changes
            with open(os.path.join(currect_dir, 'config.cfg'), 'w') as configFile:
                config.write(configFile)

            SenshudoCrawl()
    else:
        exit()

def SenshudoCrawl():
    global client, mydb

    if client is None and mydb is not None:
        print('No Client or Database...')
    else:
        mydbCursor = mydb.cursor()

        # Max Offset of 900 (see dev.twitch.tv)
        for i in range(900):
            streams = client.streams.get_live_streams(
                channel=None, 
                game=None, 
                language=None, 
                stream_type=STREAM_TYPE_LIVE, 
                limit=100, 
                offset=i
            )

            if streams is not None:
                for stream in streams:
                    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")
                    channel = GetChannel(id=stream._id)
                    game = GetGameID(gameQuery=stream.game)

                    # Update Channel Infomration
                    

            time.sleep(1)
            
def GetChannel(id):
    global client, mydb

    mydbCursor = mydb.cursor()

    mydbCursor.execute("SELECT c.id, ct.views, ct.follows, ct.modified, ct.game_id, ct.broadcast_length FROM channel AS c INNER JOIN channel_twitch AS ct WHERE ct.id = c.twitch_id AND c.twitch_id = %s", (id))
    
    return mydbCursor.fetchone()

def GetGameID(gameQuery=None):
    global client

    Games = client.search.games(query=gameQuery,live=False)

    if Games is not None:
        for Game in Games:
            if Game == gameQuery:
               return FindOrAdd(game=Game)
    else:
        return {
            'id': 0,
            'twitch_id': 0,
            'giantbomb_id': 0
        }

def FindOrAdd(game=None):
    global mydb

    if game is not None:
         mydbCursor = mydb.cursor()


        
    else:
        return {
            'id': 0,
            'twitch_id': 0,
            'giantbomb_id': 0
        }

def UpdateChannel(channel=None,game=None,stream=None):
    global mydb

    if channel is not None and stream is not None:
        mydbCursor = mydb.cursor()


# Initial Setup
SenshudoOAuth()

# Check our OAuth Token Validity every 6 Hours
schedule.every(6).hours.do(SenshudoOAuth)

# Run our Crawler every 30 minutes
schedule.every(30).minutes.do(SenshudoCrawl)

while True:
    schedule.run_pending()
    time.sleep(1)