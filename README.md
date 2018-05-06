# LoRa-sensor-data-parser
A Python program to consume sensor data coming from a MQTT broker and save it into a CSV file.

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

1. Modify the "config.cfg.sample" file according to your environment and save it as "config.cfg" file name:
```shell
[MQTT]
url	                = <LoRa Network Server's Broker URl>
port	                = <MQTT_port>
keepalive               = 60
reconnect_delay_secs    = 2
topic_id                = <MQTT_sensor_data_topic>
sim_topic               = test
username	        = <MQTT_username>
password		= <MQTT_password>

[CSV]
filename_all            = <output_log_filename_all>
filename_min            = <output_log_filename_min>
filename_hour           = <output_log_filename_hour>
filename_day            = <output_log_filename_day>

[SIMULATOR]
frequency               = 5
```

## Usage

Just run it as follows:

* The simulator:

``` shell
$ python simulator.py
```

* The people counter logger:

``` shell
$ python hirisens_people_logger.py
```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## References
