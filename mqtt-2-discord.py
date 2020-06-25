#!~/modules/venv/bin/python
#
# mqtt-2-discord
# (c) Copyright Si Dunford, June 2020 

""" 
VERSION CONTROL:
2020-06-23  V1.0.0  Initial version, basic text only
"""

"""
FURTHER READING:
https://pypi.org/project/discord-webhook/
"""

import configparser, logging, sys
import paho.mqtt.client as mqtt
from discord_webhook import DiscordWebhook

#LOG_LEVEL = logging.INFO
APPNAME = 'mqtt-2-discord'
LOG_LEVEL = logging.DEBUG
LOG_FILE = "run.log"
LOG_FORMAT ="%(asctime)s %(levelname)s %(message)s"

# INITIALISE CONFIG AND LOGGING
config = configparser.ConfigParser()
logging.basicConfig( filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL )
logging.info( "STARTING" )
topics = {}

"""
for single_input in input_list:
  try:
    single_input = int(single_input)
  except Exception as e:
    webhook = DiscordWebhook(url=webhook_url, content="in test.py line "+str(inspect.currentframe().f_lineno)+": " + str(e))
    webhook.execute()
"""

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    logging.debug( "Connected with result code "+str(rc) )

    # Subscribe to topics
    for topic in topics:
        print("* Subscribing to "+topic )
        client.subscribe(topic)

def on_message(client, userdata, msg):
    try:
        payload = str(msg.payload.decode())
        topic = msg.topic           
        if topic in topics:
            webhook_url = topics[topic]
            print( "WEBHOOK: "+webhook_url )
            webhook = DiscordWebhook( url=webhook_url, content=payload )
            webhook.execute()
    except Exception as e:
        print(e)
        
def main():
    config.read('config.ini')
    
    # Default MQTT section
    if not 'mqtt' in config:
        config['mqtt']={}
    host = config['mqtt']
    
    # Get Topics
    for key in config.sections():
        section = config[key]
        if 'topic' in section and 'webhook' in section:
            topics[section['topic']]= section['webhook']

    # Abort if there are no topics!
    if len(topics)==0:
        print( "Quitting because no topics are defined" )
        logging.critical( "No topics are defined" )
        sys.exit()
    
    # MQTT
    client = mqtt.Client( APPNAME, clean_session=False )
    hostname = host.get('host','127.0.0.1')
    hostport = host.getint('port',1883)
    if 'username' in host:
        username = host.get('username','user')
        password = host.get('password','password')
        print( "- MQTT: "+username+"@"+hostname+":"+str(hostport) )    
        client.username_pw_set( username, password )
    else:
        print( "- MQTT: "+hostname+":"+str(hostport) )    
        
    try:

        client.connect( hostname, hostport , 60 )
    except Exception as e:
        logging.critical( str(e) )
        print( e )
        sys.exit()
        
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
    client.disconnect()

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")
        print( "Terminated by user" )
        sys.exit()
