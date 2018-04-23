# LoRa-sensor-data-parser
A Python program to consume sensor data coming from a MQTT broker into a CSV file.

## Table of Contents
 - [Installation](#installation)
 - [Configuration](#configuration)
 - [Usage](#usage)
 - [Contributing](#contributing)
 - [References](#references)

## Installation

First of all install the required Python libraries for MQTT:
```shell
    $ sudo pip install paho-mqtt
```

## Configuration

The following tweaks are needed in order to make it work:

1. Modify the "config.cfg" file according to your environment:
```shell
[MQTT]
url	                    = <LoRa Network Server's Broker URl>
port	                  = <MQTT Broker port>
keepalive               = 60
reconnect_delay_secs    = 2
topic_id                = <Broker topic to subscribe>
username	              = <MQTT Broker username>
password		            = <MQTT Broker password>

[CSV]
filename	              = output/people_counter.csv
```

## Usage

Just run it as follows:
``` shell
$ python subscribe_mqtt.py
```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## References
