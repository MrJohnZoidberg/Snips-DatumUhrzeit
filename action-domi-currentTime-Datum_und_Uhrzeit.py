#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import datetime

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)

import os.path

def readStringFromFile():
    home = os.path.expanduser("~")
    fname = home + '/snips-strings/action-domi-currentTime-Datum_und_Uhrzeit.txt'
    if os.path.isfile(fname):
        with open(fname, 'r') as file:
            return file.read()
    else:
        string = "Es ist {hours} Uhr {minutes} und {seconds} Sekunden."
        if not os.path.exists(os.path.dirname(fname)):
            try:
                os.makedirs(os.path.dirname(fname))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise 
        with open(fname, 'w') as file:
            file.write(string)
        return string

    
def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined 

    Refer to the documentation for further details. 
    """ 
    hours = datetime.datetime.now().hour
    minutes = datetime.datetime.now().minute
    seconds = datetime.datetime.now().second
    if hours == 1:
        result_sentence = "Gerade ist es ein Uhr {0} und {1} Sekunden.".format(minutes, seconds)
    else:
        result_sentence = readStringFromFile().format(hours=hours, minutes=minutes, seconds=seconds)
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("domi:currentTime", subscribe_intent_callback) \
.start()
