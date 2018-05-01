"""Program to simulate hirisense people counter data by publishing test data on Mosquitto MQTT broker."""
# Importing the PAHO MQTT Client Class
import paho.mqtt.client as mqtt
import ConfigParser
import time
import os
import sys
import time
import json
import base64
from random import randint

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
    ret["sim_topic"] = config.get('MQTT', 'sim_topic')
    ret["username"] = config.get('MQTT', 'username')
    ret["password"] = config.get('MQTT', 'password')
    ret["csv_file"] = config.get('CSV', 'filename')
    ret["frequency"] = config.get('SIMULATOR', 'frequency')

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
    ret["qos_pub"] = 0

    # "Retain Flag" (RF) status:
    #   retain = False (Default) ==> Last Message NOT sent
    #   retain = True            ==> Last Message sent
    ret["rf"] = False

    return ret

################################
# Connection Return Codes (RC) #
################################
#
#   0: Connection successful
#   1: Connection refused - incorrect protocol version
#   2: Connection refused - invalid client identifier
#   3: Connection refused - server unavailable
#   4: Connection refused - bad username or password
#   5: Connection refused - not authorised


################################
# MQTT Callback Functions      #
################################
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
        client.loop_stop()
        sys.exit()


def on_disconnect(client, userdata, flags, rc=0):
    """on_disconnect callback function."""
    client.connected_flag = False
    client.disconnect_flag = True
    print("Disconnected!!")


def on_publish(client, userdata, mid):
    """on_publish callback function."""
    print("Data published with MID: " + str(mid)) + "\n"


def dec2hex(datadec):
    """Convert decimal data into two hexadecimal bytes."""
    if data_dec < 16:
        prefix = "000"
    elif datadec > 15 & datadec < 256:
        prefix = "00"
    elif datadec > 255 & datadec < 4096:
        prefix = "0"
    elif datadec > 4095 & datadec < 6553:
        prefix = ""

    res = prefix + str(format(datadec, 'x'))
    return res


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
    client = mqtt.Client("Pub", conf["csf"])

    # Binding of MQTT callback functions Assign: "on_connect" | "on_subscribe" |
    # | "on_message"
    client.on_connect = on_connect
    client.on_publish = on_publish

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
        ################################
        # LOOPS                        #
        ################################
        #
        # General Note: Strange behaviour when starting a loop before creating a
        # connection.
        #
        # LOOP_START() | LOOP_STOP()
        # --------------------------
        #
        # Description: The loop_start() starts a new thread, that calls the loop method
        # at regular intervals for you. It also handles re-connects automatically. To
        # stop the lopp "loop_stop()".
        #
        client.loop_start()

        # LOOP_FOREVER()
        # --------------
        #
        # Description: "loop_forever()" is blocking, which means the client will
        # continue to print out incoming message information until the program is
        # killed. This method blocks the program, and is useful when the program must
        # run indefinitely.
        #
        # client.loop_forever()

        ################################
        # PUBLISH                      #
        ################################
        # Publish Structure: publish(topic, payload=None, qos=0, retain=False)
        lora_message = {
                        "applicationID":"5",
                        "applicationName":"Hirisens_CP",
                        "deviceName":"ConteoPersonas",
                        "devEUI":"0004a30b0022889e",
                        "rxInfo":[
                                    {
                                     "mac":"7276ff002e062700",
                                     "rssi":-58,
                                     "loRaSNR":9.5,
                                     "name":"Kerlink_iBTS_GW1",
                                     "latitude":28.0916,
                                     "longitude":-17.1133,
                                     "altitude":0
                                    }
                                ],
                        "txInfo":{
                                   "frequency":868500000,
                                   "dataRate":
                                             {
                                              "modulation":"LORA",
                                              "bandwidth":125,
                                              "spreadFactor":7
                                             },
                                    "adr":"true",
                                    "codeRate":"4/5"
                                 },
                        "fCnt":27,
                        "fPort":1,
                        "data":""
                      }
        time.sleep(2)
        while True:
            # raw_input("Press Enter to continue...")
            # We are limiting random data to values between 0-100 instead of 0-65535
            data_dec = randint(0,100)
            print("Decimal: " + str(data_dec))

            data_hex = dec2hex(data_dec)
            print("Hexadecimal: " + str(data_hex))

            data_complete_hex = "0a" + data_hex + "ddffff200020"

            # data_complete_hex = "0a" + data_hex
            print("Hex Completo: " + data_complete_hex)

            # data_complete_coded = base64.b64encode(data_complete_hex)
            data_complete_encoded = data_complete_hex.decode("hex").encode("base64")
            data_complete_encoded = data_complete_encoded.rstrip()
            print("Hex Completo Codificado: " + data_complete_encoded)

            lora_message['data'] = data_complete_encoded

            (rc, mid) = client.publish(conf["sim_topic"], json.dumps(lora_message), conf["qos_pub"], conf["rf"])

            time.sleep(float(conf["frequency"]))
    except:
        print("Connection Failed. Please check MQTT broker URL on 'config.cfg' file.")
