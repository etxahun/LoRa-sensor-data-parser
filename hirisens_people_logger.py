"""Program to subscribe to a topic of a Mosquitto MQTT broker."""
# Importing the PAHO MQTT Client Class
import paho.mqtt.client as mqtt
import ConfigParser
import os
import platform
import pprint
import json
import base64
import csv
from datetime import *

################################
# Global Configuration          ###############################################
################################
def loadConf():
    """Load configuration data from the 'locate.cfg' file."""

    ret = {}

    config = ConfigParser.ConfigParser()
    config.read("config.cfg")

    # MQTT Settings
    ret["broker_address"] = config.get('MQTT', 'url')
    ret["broker_port"] = int(config.get('MQTT', 'port'))
    ret["keepalive"] = int(config.get('MQTT', 'keepalive'))
    ret["topic_id"] = config.get('MQTT', 'topic_id')
    ret["username"] = config.get('MQTT', 'username')
    ret["password"] = config.get('MQTT', 'password')
    ret["csv_file"] = config.get('CSV', 'filename')

    # Data Persistence configuration:
    # "Clean Session" Flag (CSF):
    #   Clean Session = True  (Default) ==> No Persistence activated
    #   Clean Session = False           ==> Persistence activated
    ret["csf"] = True

    # QoS of Subscriber:
    #   QoS = 0 (Default) ==> "Fire and forget"
    #   QoS = 1           ==> Message will be delivered AT LEAST ONCE (PUBLISHC
    #                         AND PUBACK)
    #   QoS = 2           ==> Guarantees that the message is received ONLY ONCE
    #                         by the counterpart. Safest but slowest.
    ret["qos_sub"] = 0

    return ret

########
# MQTT #########################################################################
########

# ------------------------------
# Connection Return Codes (RC) |-----------------------------------------------
# ------------------------------
#   0: Connection successful
#   1: Connection refused - incorrect protocol version
#   2: Connection refused - invalid client identifier
#   3: Connection refused - server unavailable
#   4: Connection refused - bad username or password
#   5: Connection refused - not authorised


# ------------------------------
# MQTT Callback Functions      |-----------------------------------------------
# ------------------------------
def on_connect(client, userdata, flags, rc):
    """on_connect callback function."""
    if rc == 0:
        # Set "connected" flag
        client.connected_flag = True
        print("CONNACK received with code %d.\n" % (rc))
    else:
        # Set "bad_connection" flag
        client.bad_connection_flag = True
        print("Bad connection. Returned code %d.\n" % (rc))


def on_disconnect(client, userdata, flags, rc=0):
    """on_disconnect callback function."""
    client.connected_flag = False
    client.disconnect_flag = True
    print("Disconnected!!")


def on_subscribe(client, userdata, mid, granted_qos):
    """on_subscribe callback function."""
    # The "granted_qos" parameter contains a list of the granted QoS (or
    # failure) codes sent by the broker
    print("Subscribed: \t MID: " + str(mid) + "\t Granted QoS: " + str(granted_qos))


def on_message(client, userdata, msg):
    """on_message callback function.

    'msg' structure:
                    {
                     "applicationID":"5",
                     "applicationName":"Hirisens",
                     "deviceName":"ConteoPersonas",
                     "devEUI":"0004a30b0022889e",
                     "rxInfo":[
                                {
                                 "mac":"7276ff002e062700",
                                 "rssi":-59,
                                 "loRaSNR":8.5,
                                 "name":"Kerlink_iBTS_GW1",
                                 "latitude":28.0916,
                                 "longitude":-17.1133,
                                 "altitude":0
                                 }
                              ],
                     "txInfo":{
                                "frequency":868100000,
                                "dataRate":
                                           {
                                            "modulation":"LORA",
                                            "bandwidth":125,
                                            "spreadFactor":7
                                           },
                                "adr":true,
                                "codeRate":"4/5"
                               },
                     "fCnt":9,
                     "fPort":1,
                     "data":"CgAA3f//IABj"
                    }
    """
    data = json.loads(msg.payload)
    # pprint.pprint(data) # Pretty Print

    # Step 1: Payload raw data (base64 encoded):
    payload_raw = data['data']

    # Step 2: Payload decoded Base64 to Hex:
    payload_hex = base64.b64decode(payload_raw)
    # Resulting payload:
    #   '\n\x00\x00\xdd\xff\xff \x00c'


    # Step 2 (Alternative): If we want to decode in a more readable format:
    # payload_hex = base64.b64decode(payload_raw).encode('hex')
    # Resulting payload:
    #  '0a0000ddffff200063'

    # Step 3: Payload stored as byte string:
    payload_hex = ":".join("{:02x}".format(ord(c)) for c in payload_hex)
    # Resulting payload::
    #   '0a:00:00:dd:ff:ff:20:00:63'
    # print("Payload split: " + str(payload_hex))

    # Step 4: Payload stored as list of bytes:
    payload_decoded = payload_hex.split(":")
    # print("Payload List: " + str(payload_decoded))
    # print ("Primer Byte: " + str(payload_decoded[0]))

    # Step 4 (Alternative): Store data obtained in "Step 2 (Alternative)" as
    # a list ob objects:
    # payload_decoded = [payload_hex[i:i+2] for i in range(0, len(payload_hex), 2)]

    if payload_decoded[0] == "0a":
        # People counter data extraction (second and third bytes):
        counter_hex = payload_decoded[1] + payload_decoded[2]
        counter_dec = int(counter_hex, 16)

        # Debug:
        print("\nTopic: " + str(msg.topic) +
              "\nQoS: " + str(msg.qos) +
              "\nPayload (base64): " + str(payload_raw) +
              "\nPayload (Hex): " + str(payload_decoded) +
              "\nPeople Counter: " + str(counter_dec) + "\n")

    else:
        print "No Data available!"
        counter_dec = -1

    # Save data to CSV file:
    save2csv(counter_dec)

def save2csv(number):
    """stored people counter data on CSV file.

            CSV file format: TimeStamp, counter_value
    """

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # headers=['timestamp', 'counter']
    with open(conf['csv_file'], 'a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',lineterminator='\n')
        filewriter.writerow([timestamp, number])
    csvfile.close()


if __name__ == '__main__':
    # Load general configuration:
    conf = loadConf()

    #-------------------------------
    # MQTT Callback Functions      |
    #-------------------------------

    # Create client object persistent connection (clean_session=False)
    # Structure: Client(client_id='', clean_session=True,
    #                   userdata=None, protocol=MQTTv311, transport='tcp')
    #
    client = mqtt.Client("Sub", conf["csf"])

    # Binding of MQTT callback functions Assign: "on_connect" | "on_subscribe" |
    # | "on_message"
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    # Clear Screen:
    os_version = platform.system()
    if os_version == 'Windows':
        os.system('cls')
    elif os_version in ('Linux', 'Darwin'):
        os.version('clear')

    # Connect to Broker and Publish
    print("Connecting to broker " + str(conf["broker_address"]) + "...")
    # Without Username/Password:
    # client.connect(broker_address, port)

    # With Username/Password:
    client.username_pw_set(conf["username"], conf["password"])
    try:
        client.connect(conf["broker_address"], conf["broker_port"])
        #-------------------------------
        # SUBSCRIBE                    |
        #-------------------------------
        #
        # Subscribe Structure: subscribe(topic, qos=0)
        client.subscribe(conf["topic_id"], conf["qos_sub"])


        # -------------------------------
        # LOOPS                         |
        #--------------------------------
        #
        # General Note: Strange behaviour when starting a loop before creating a
        # connection.
        #
        # LOOP_START() | LOOP_STOP()
        # --------------------------
        #
        # Description: The loop_start() starts a new thread, that calls the loop
        # method at regular intervals for you. It also handles re-connects
        # automatically.To stop the lopp "loop_stop()".
        #
        # client.loop_start()

        # LOOP_FOREVER()
        # --------------
        #
        # Description: "loop_forever()" is blocking, which means the client will
        # continue to print out incoming message information until the program is
        # killed. This method blocks the program, and is useful when the program must
        # run indefinitely.
        #
        client.loop_forever()
    except:
        print("Connection Failed. Please check MQTT broker URL on 'config.cfg' file.")
