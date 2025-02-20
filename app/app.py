"""
This script python get and will run the RL algorithm
"""
#!/usr/bin/env python3
# coding: utf-8
#
# Script to run the RL Algorithm. It'll use paho mqtt to get data from the network server.
#
# ===
#
# ===
# Notes
#
# ===
# feb.24  release

# Codding and RN2483 integration: A.MORAL
# Model conception and RL training : M. BATTA
# Test and Supervision: R. KACIMI

#############################################################################
#
# Import zone
#
import logging
import os
from time import sleep
from pathlib import Path
#Socket for execption handling
import socket
import json

#Threads
from queue import Queue

from itertools import product
import pickle

import datetime

import numpy as np

from dotenv import load_dotenv
import paho.mqtt.client as paho

from RN2483 import RN2483

# #############################################################################
#
# Configuration
#
logging.basicConfig(
    level=logging.DEBUG,
            format='%(asctime)s,%(msecs)03d %(levelname)-8s - [%(filename)s.%(funcName)-10s:\
%(lineno)-3d.] - %(message)s')

#Get the server and node credentials from a .env file
#Get .env name
node_str = os.getenv('NODE')
logging.debug("%s",node_str)

dotenv_path = Path(f"./files_env/{node_str}")
load_dotenv(dotenv_path=dotenv_path)

DEVADDR = os.getenv('DEVADDR')
APPSKEY = os.getenv('APPSKEY')
NWKSKEY = os.getenv('NWKSKEY')

MQTT_SERVER = os.getenv('MQTT_SERVER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC    = os.getenv('MQTT_TOPIC')


PORT = "/dev/ttyACM0"

Q_TABLE_PATH = './config/Q_model-LORA-rob.pkl'

#Create Queue for MQTT
mqtt_queue = Queue()

#Max number of transmissions
MAX_TRANSMISSIONS = 50

#Get experiment start time
TIME_START = datetime.datetime.now()
START_EXP = TIME_START.strftime("%m%d%Y-%H:%M:%S")

# #############################################################################
#
# MQTT functions
#

def connect_to_broker(max_number_of_tries:int):
    """
    Function that initiate a broker connection
    Param :
        max_number_of_tries:int : Max number of tries before considering impossible to connect
            to broker
    Returns:
        mqtt_client:paho.mqtt.client.Client : Client we tried to connect to the broker
    """

    #Check if we can connect
    errors_count = 0
    f_connected =   False
    while not f_connected:
        try :
            mqtt_client = paho.Client()
            mqtt_client.connect(MQTT_SERVER,port=MQTT_PORT)
            mqtt_client.username_pw_set(username=MQTT_USERNAME,password=MQTT_PASSWORD)

            mqtt_client.loop_start()
            sleep(0.1)
            f_connected = True
        except (socket.error) as error:
            errors_count+=1
            logging.error("While connecting to broker, %s : %s ",error.__class__,error)
            sleep(1)
            if errors_count >= max_number_of_tries:
                logging.critical("Could not connect to broker, address is %s and\
 port is %s.Error : %s : %s",MQTT_SERVER,MQTT_PORT,error.__class__,error)
                raise error

    return mqtt_client

def wait_connection(mqtt_client:paho.Client,max_number_of_tries:int):
    """
    Simple function to wait for connection.
    If it fails after max_number_of_tries tries, return False else True
    Param :
        mqtt_client:paho.Client : A paho.Client 
        max_number_of_tries:int : Number of tries before returning False
    Returns :
        bool : True if connected, else False
    """
    errors_count = 0
    while mqtt_client.is_connected() is False :
        #Wait for connection
        errors_count += 1
        sleep(1)

        if errors_count >= max_number_of_tries:
            return False
    return True

def mqtt_connect():
    """
    Function that tries to connect to a broker and return mqtt_client

    Returns:
        mqtt_client:paho.Client : The mqtt_client for the connection
    """

    #Connect to Broker
    try :
        mqtt_client = connect_to_broker(5)
    except (socket.error) as error:
        logging.critical("Could not connect to broker, address is %s and\
 port is %s.Error : %s : %s",MQTT_SERVER,MQTT_PORT,error.__class__,error)
        #End related threads
        raise RuntimeError("Could not connect to MQTT Broker") from error

    #Wait for connection
    connect_status = wait_connection(mqtt_client,5)
    if not connect_status :
        logging.critical("Could not connect to broker, address is %s and port is %s",
                            MQTT_SERVER,MQTT_PORT)
        #End related threads
        raise RuntimeError("Could not connect to MQTT Broker")

    return mqtt_client

def mqtt_on_message(client:paho.Client,userdata:any,message:paho.MQTTMessage):
    """
    Call back function when the MQTT Client get a message
    Intended usage : function assigned to a paho.Client.on_message
    Params : 
        client:paho.Client : Client paho mqtt
        userdata:any : Userdata
        message:paho.MQTTMessage : Message from the MQTT Broker (expected Chirpstack)
    """
    #logging.debug("Got a message : \n Client : %s\nUser data : %s\nmessage : %s"
    #              ,client,userdata,message.payload)
    try :
        #Filename
        filename:str = f"./logs/exp-{START_EXP}_mqtt.txt"

        #Save start
        with open(filename,"a+",encoding="utf-8") as file:
            json_data = json.loads(message.payload)
            json.dump(json_data,file)
            file.write("\n")
            if json_data["devaddr"]==DEVADDR:
                mqtt_queue.put(json_data,block=True,timeout=None)
    except ValueError:
        #Not a json
        logging.info("NO JSON = Message : %s",message.payload)

# #############################################################################
#
# Functions
#

def q_model(snr:int,tp:int):
    """
    Function exploiting the Q-Table made by experimentations.
    Params:
        snr:int : Signal To Noise Ratio
        tp:int : PWRIDX from 1 to 5, representing differents power level
    Returns :
        (datarate,transmission_power)
        datarate:int: Datarate for the module to use from 0 to 5
        transmission_power:int : Transmission power for the module to use
            from 1 to 5.
    """
    #Power levels in dbm
    power_levels = [6, 8, 10, 12, 14]
    #Available SF, 
    sfs= [7, 8, 9, 10, 11, 12, 13]
    #Space computed 0
    snr_space = np.linspace(6.5 ,-20.5, int((6.5+20.5)*2 + 1))
    actions = list(product(sfs, power_levels))
    #Convert dbm to TP
    mapping_tp = {6: 5, 8: 4, 10: 3, 12: 2, 14: 1}
    #Use the Q-Table and load it 
    with open(Q_TABLE_PATH, 'rb') as f:
        q_table = pickle.load(f)

    q_value = np.argmax(
                q_table[min(np.digitize(snr, snr_space), 54),
                np.digitize(tp, power_levels) -1,:]
                )
    logging.debug("SF:%s",actions[q_value][0])
    logging.debug("TP:%s",actions[q_value][1])
    transmission_power = mapping_tp[actions[q_value][1]]
    datarate=actions[q_value][0]
    return datarate , transmission_power


# #############################################################################
#
# Main
#

def main():
    #Main function of the program

    # MQTT
    #Connect to Broker
    try :
        mqtt_client = mqtt_connect()
    except RuntimeError as error:
        logging.critical("Could not connect to broker, %s",error)
        return 1
    mqtt_client.on_message = mqtt_on_message
    logging.info("Connected to MQTT Broker.")

    #Sub to topic
    mqtt_client.subscribe(MQTT_TOPIC)

    #Create an object
    module = RN2483(PORT)

    #Number of messages sent
    nb_transmissions = 0
    #Choose parameter
    selected_dr=0
    selected_tp=1

    #Filename
    filename:str = f"./logs/exp-{START_EXP}_data.txt"

    #Save start
    with open(filename,"a+",encoding="utf-8") as file:
        file.write(f"Starting experimentation at time:{START_EXP}\n")

    #Factory Reset
    logging.info("Starting Factory Reset")
    status_code=1
    while status_code == 1:
        (status_code,response) = module.factory_reset()
        logging.info("Facto reset : %s,%s",status_code,response)

    #Set parameters
    #Config savable parameters
    logging.info("Setting Savable Params ABP")
    (status_code,response) = module.config_savable_parameters_abp(DEVADDR,NWKSKEY,
                                                            APPSKEY,0,{0:0,1:0,2:0})
    logging.info("Savable parameters response : %s,%s",status_code,response)

    #Join network
    logging.info("Join network ABP")
    (status_code,response) = module.join_network(True)
    logging.info("Savable parameters response : %s,%s",status_code,response)

    # Main loop
    while nb_transmissions<MAX_TRANSMISSIONS:
        #Config transmission parameters
        module_dr = -1
        module_tp = -1
        #While mqtt_queue is empty send messages
        while mqtt_queue.empty() and nb_transmissions<MAX_TRANSMISSIONS:
            #Send message
            #Get datarate
            got_error=1
            while got_error == 1:
                (got_error,module_dr) = module.get_datarate()

            #Get pwridx
            got_error=1
            while got_error == 1:
                (got_error,module_tp) = module.get_pwridx()

            if module_dr!=selected_dr or module_tp!=selected_tp:
                #Config transmission parameters
                logging.info("Setting Transmission parameters")
                (status_code,response) = module.config_transmission_parameter(selected_dr,False,
                                            selected_tp)
                logging.info("Transmission parameters response : %s,%s",status_code,response)
                if status_code == 1:
                    raise RuntimeError("Invalid transmission parameters")

            #Format data
            data = {"DR":selected_dr,"TP":selected_tp,"N":nb_transmissions}
            json_string = json.dumps(data)
            logging.debug("%s",json_string)

            logging.info("Sending %s",json_string)
            #Send the datarate
            (status_code,response,_) = module.send_uplink(json_string,False)

            nb_transmissions+=1

        #Check if we did enough transmissions
        if nb_transmissions>=MAX_TRANSMISSIONS:
            break

        #We got a MQTT message
        mqtt_message = mqtt_queue.get()
        #Empty the queue
        while not mqtt_queue.empty():
            mqtt_queue.get()
        #Get lsnr
        lsnr = float(mqtt_message['best_gw']['lsnr'])
        logging.debug("LSNR : %s",lsnr)

        #Send lsnr and transmission power to the function
        (sf,new_tp)=q_model(lsnr,selected_tp)
        new_dr= 12-sf

        #Save to file
        if new_tp!=selected_tp or new_dr!=selected_dr:
            logging.info("[DSF2R] Datarate %s to %s\t\tTransmission Power %s to %s",
                            selected_dr,new_dr,selected_tp,new_tp)
            logging.info("Best gateway : %s",mqtt_message['best_gw']["desc"])
            with open(filename,"a",encoding="utf-8") as file:
                t_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                file.write(f"{t_time} :[DSF2R] Datarate {selected_dr} to {new_dr}\t\t\
Transmission Power {selected_tp} to {new_tp} - Nb message : {nb_transmissions} - \
Best GW {mqtt_message['best_gw']['desc']}- snr : {lsnr}\n")

        selected_tp=new_tp
        selected_dr=new_dr

    end_exp = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    with open(filename,"a",encoding="utf-8") as file:
        file.write(f"End of experimentation,time:{end_exp}")

if __name__ == "__main__":
    logging.info("Starting experimentation")
    main()
