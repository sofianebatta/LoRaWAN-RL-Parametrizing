"""
    This module is used to create the RN2483 Class
"""
#!/usr/bin/env python3
# coding: utf-8
#
# RN2483
#
# ===
# Todo
# - Add crc header
# - Add coding rate control
# ===
# Notes
#
# ===
# M.Alexandre   oct.24  creation
#

# #############################################################################
#
# Import zone
#

import time
from typing import Dict
import datetime
import logging
import serial

# #############################################################################
#
# Global Variables & Configs
#

#Logger
logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s,%(msecs)03d %(levelname)-8s - [%(filename)s:%(lineno)d] - \
%(threadName)s - %(message)s')

# #############################################################################
#
# Class RN2483
#

class RN2483( serial.Serial ):
    """
    Class for sending commands to the RN2483 module
    Aim to parse the answers
    """
    def __init__(self,port,baudrate=57600):
        #Open the communication
        serial.Serial.__init__(
            self,port=port, baudrate=baudrate,
            bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
            timeout=1, xonxoff=False, rtscts=False, write_timeout=None,
            dsrdtr=False, inter_byte_timeout=None, exclusive=None
        )

    def send_command(self,data:str,timeout:int=10):
        """
        Method used for sending a command to the module
        TODO : write docstring
        """
        #Encode data and send it through the serial connection
        data_to_send = (data.rstrip()+"\x0d\x0a").encode()
        self.write(data_to_send)
        time.sleep(0.2)

        #Wait for a response
        response = []
        status_code = -1
        start_time = datetime.datetime.now()
        while status_code==-1:
            #Check if something is being received
            if self.in_waiting:
                line = self.readline()
                if line !=b'\r\n':
                    #Decode line and remove leading + trailing whitespaces
                    decoded_line = line.decode('utf-8').strip()
                    logging.debug("Decoded line : %s",decoded_line)
                    response.append(decoded_line)
                    if 'ok' in decoded_line :
                        status_code=0
                    elif 'invalid_param' in decoded_line:
                        status_code=1
                    elif 'keys_not_init' in decoded_line:
                        status_code=1
                    elif 'no_free_ch'in decoded_line:
                        status_code=1
                    elif 'silent'in decoded_line:
                        status_code=1
                    elif 'busy'in decoded_line:
                        status_code=1
                    elif 'mac_paused'in decoded_line:
                        status_code=1
                    elif 'not_joined'in decoded_line:
                        status_code=1
            if (datetime.datetime.now() - start_time).seconds > timeout:
                status_code=3
            time.sleep(0.3)

        if response and status_code==3:
            status_code=0

        #Decode response and send it
        logging.debug("Decoded response : %s",response)
        return (status_code,response)

    def factory_reset(self):
        """
        Method to factory reset the module.
            This command resets the module’s configuration data and user EEPPROM to factory
        default values and restarts the module. After factoryRESET, the RN2483 module will
        automatically reset and all configuration parameters are restored to factory default
        values.
            Response: RN2483 X.Y.Z MMM DD YYYY HH:MM:SS, where X.Y.Z is firmware
        version, MMM is month, DD is day, HH:MM:SS is hour, minutes, seconds (format: [HW]
        [FW] [Date] [Time]). [Date] and [Time] refer to the release of the firmware.
        Params:
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command("sys factoryRESET",timeout=5)
        logging.debug("FACTORYRESET : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def reset(self):
        """
        Method to reset the module.
            This command resets and restarts the RN2483 module; stored internal configurations
        will be loaded automatically upon reboot.
            Response: RN2483 X.Y.Z MMM DD YYYY HH:MM:SS, where X.Y.Z is firmware
        version, MMM is month, DD is day, HH:MM:SS is hour, minutes, seconds (format: [HW]
        [FW] [Date] [Time]). [Date] and [Time] refer to the release of the firmware.
        Params:
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command("sys reset",timeout=5)
        logging.debug("RESET : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_deveui(self,deveui:str):
        """
        Method to set the deeui.
            This command sets the globally unique device identifier for the module. The identifier
        must be set by the host MCU
            If this parameter was previously saved to user EEPROM by issuing the
        mac save command, after modifying its value, the mac save command
        should be called again.
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            deveui:str : 8-byte hexadecimal number representing the device EUI
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set deveui {deveui}",timeout=5)
        logging.debug("SET DEVEUI : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_appeui(self,appeui:str):
        """
        Method to set the appeui. APPEUI is the same thing as JOINEUI.
            This command sets the application identifier for the module. The application identifier
        should be used to identify device types (sensor device, lighting device, etc.) within the
        network.
            If this parameter was previously saved to user EEPROM by issuing the
        mac save command, after modifying its value, the mac save command
        should be called again.
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            appeui:str : 8-byte hexadecimal number representing the application EUI
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set appeui {appeui}",timeout=5)
        logging.debug("SET APPEUI : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_appkey(self,appkey:str):
        """
        Method to set the appkey. 
            This command sets the application key for the module. The application key is used to
        identify a grouping over module units which perform the same or similar task
            If this parameter was previously saved to user EEPROM by issuing the
        mac save command, after modifying its value, the mac save command
        should be called again.
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            appkey:str : 16-byte hexadecimal number representing the application key
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set appkey {appkey}",timeout=5)
        logging.debug("SET APPKEY : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_pwridx(self,pwr_index:int):
        """
        Method to set the output power.
            This command sets the output power to be used on the next transmissions

            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            pwr_index:int : 
                decimal number representing the index value for the output power,
                    from 1 to 5 for 868 MHz
                    frequency band.
                    1 - is max
                    5 - is min
                
                Note : In the document it is said that 1 is 14 dBm but I got 20 dBm with a
                device using 5V.
                Also, I've found that :
                    1 Max EIRP         = 14 dBm
                    2 Max EIRP - 2dB   = 12 dBm
                    3 Max EIRP - 4dB   = 10 dBm
                    4 Max EIRP - 6dB   = 8  dBm
                    5 Max EIRP - 8dB   = 6  dBm
            but that was not what we measured. 

        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set pwridx {pwr_index}",timeout=5)
        logging.debug("SET PWRIDX : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_datarate(self,datarate:int):
        """
        Method to set the datarate. 
            This command sets the data rate to be used for the next transmission.
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            datarate:int : decimal number representing the data rate, from 0 and 7, but within the
                limits of the data rate range for the defined channels
                - 0 LoRa: SF12 / 125 kHz 250
                - 1 LoRa: SF11 / 125 kHz 440
                - 2 LoRa: SF10 / 125 kHz 980
                - 3 LoRa: SF9 / 125 kHz 1760
                - 4 LoRa: SF8 / 125 kHz 3125
                - 5 LoRa: SF7 / 125 kHz 5470

        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set dr {datarate}",timeout=5)
        logging.debug("SET DATARATE : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    #TRY TO GET ADR TO SEE IF IT DOES SOMETHING
    def set_adr(self,adr_state:bool):
        """
        Method to enable/disable the ADR. 
            This command sets if the adaptive data rate (ADR) is to be enabled, or disabled. The
        server is informed about the status of the module’s ADR in every uplink frame it
        receives from the ADR field in uplink data packet. If ADR is enabled, the server will
        optimize the data rate and the transmission power of the module based on the
        information collected from the network.
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            adr_state:bool : If true we set the adr, if not we disable it
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        if adr_state:
            command = 'on'
        else:
            command = 'off'
        (status_code,response) = self.send_command(f"mac set adr {command}",timeout=5)
        logging.debug("SET ADR : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_linkchk(self,time_interval:int):
        """
        Method to set the time interval for the link check or disable it. 
            This command sets the time interval for the link check process to be triggered
            periodically. A <value> of '0' will disable the link check process. When the time
            interval expires, the next application packet that will be sent to the server will 
            include also a link check MAC command.
            Response:   ok if address is valid
                        invalid_param if address is not valid
            If this parameter was previously saved to user EEPROM by issuing the
            mac save command, after modifying its value, the mac save command
            should be called again.
        Params:
            time_interval:int : decimal number that sets the time interval in seconds for
                the link check process, from 0 to 65535
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set linkchk {time_interval}",timeout=5)
        logging.debug("SET LINKCHECK : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_rx1_delay(self,rx1_delay:int):
        """
        Method to set the rx delay.
            This command will set the delay between the transmission and the first Reception
        window to the <rxDelay> in milliseconds. The delay between the transmission and
        the second Reception window is calculated in software as the delay between the
        transmission and the first Reception window + 1000 (ms).
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            time_interval:int : decimal number representing the delay between the 
            transmission and the first Reception window in milliseconds,
            from 0 to 65535
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set rxdelay1 {rx1_delay}",timeout=5)
        logging.debug("SET RXDELAY : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_rx2_params(self,datarate:int,frequency:int):
        """
        Method to set the transmission parameters of the second receive window.
            This command sets the data rate and frequency used for the second Receive window.
        The configuration of the Receive window parameters should be in concordance with
        the server configuration.
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
            datarate:int : decimal number representing the data rate, from 0 to 7
            frequency:int : decimal number representing the frequency, from 863000000 to
            870000000 or from 433050000 to 434790000, in Hz.
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set rx2 {datarate} {frequency}",timeout=5)
        logging.debug("SET RX2PARAMS : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_dutycycle(self,channel_id:int,duty_cycle_percentage:int):
        """
        Method to set the duty cycle.
            This command sets the duty cycle used on the given channel ID on the module
            Response:   ok if address is valid
                        invalid_param if address is not valid
            If this parameter was previously saved to user EEPROM by issuing the
            mac save command, after modifying its value, the mac save command
            should be called again.
        Params:
            channel_id:int :  decimal number representing the channel number, from 0 to 15
            dutycycle_percentage:int : percentage representing the duty cycle you want. 
                If you input 0, the duty cycle will be 100%
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        #Compute dutycycle
        if duty_cycle_percentage == 0:
            d_cycle_param = 0
        else:
            logging.debug("Val : %s",int(100.0/duty_cycle_percentage)-1)
            d_cycle_param = int(100.0/duty_cycle_percentage)-1

        logging.debug("d_cycle_param : %s",d_cycle_param)

        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command(f"mac set ch dcycle {channel_id} {d_cycle_param}"
                                                    ,timeout=5)
        logging.debug("SET DCYCLE PARAMS : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_channel_status(self,channel_id:int,status:bool):
        """
        Method to Enable or Disable channels.
            Response:   ok if address is valid
                        invalid_param if address is not valid
                If this parameter was previously saved to user EEPROM by issuing the
            mac save command, after modifying its value, the mac save command
            should be called again.
                Warning: <ChannelId> parameters (frequency, data range, duty cycle) must be
            issued prior to enabling the status of that channel.
        Params:
            channel_id:int :  decimal number representing the channel number, from 0 to 15
            status:bool : if True, enable the channel, else disable it
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        #Compute dutycycle
        if status :
            channel_state = "on"
        else:
            channel_state = "off"

        response    = []
        status_code = 1

        #Send the command
        (status_code,response)= self.send_command(f"mac set ch status {channel_id} {channel_state}",
                                timeout=5)
        logging.debug("SET CHANNEL STATUS : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_cnf_retransmissions(self,nb_rx:int):
        """
        Method to set the number of retransmissions if a message
        is not confirmed when sent in cnf mode.
            This command sets the number of retransmissions to be used for an uplink confirmed
        packet, if no downlink acknowledgment is received from the server.
            Response: ok if <retx> is valid
                invalid_param if <retx> is not valid
        Params:
            nb_rx:int : decimal number representing the number of retransmissions for an uplink
                confirmed packet, from 0 to 255.
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response)= self.send_command(f"mac set retx {nb_rx}",
                                timeout=5)
        logging.debug("SET RETX : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_dev_addr(self,devaddr:str):
        """
        Method to set dev addr (ABP)
            This command configures the module with a 4-byte unique network device address
        <address>. The <address> MUST be UNIQUE to the current network. This must be
        directly set solely for activation by personalization devices. This parameter must not be
        set before attempting to join using over-the-air activation because it will be overwritten
        once the join process is over.
            Response: ok if adress is valid
                invalid_param if adress is not valid
        Params:
            devaddr:str : 4-byte hexadecimal number representing the device address, from
                00000000 – FFFFFFFF
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response)= self.send_command(f"mac set devaddr {devaddr}",
                                timeout=5)
        logging.debug("SET DEVADDR : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_network_session_key(self,nwkskey:str):
        """
        Method to set the network session key (ABP)
            This command sets the network session key for the module. This key is 16 bytes in
        length, and should be modified with each session between the module and network.
        The key should remain the same until the communication session between devices is
        terminated.
            Response: ok if adress is valid
                invalid_param if adress is not valid
        Params:
            nwkskey:str : 16-byte hexadecimal number representing the network session key
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response)= self.send_command(f"mac set nwkskey {nwkskey}",
                                timeout=5)
        logging.debug("SET NWSKEY : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def set_application_session_key(self,appskey:str):
        """
        Method to set the application session key (ABP)
            This command sets the application session key for the module. This key is unique,
        created for each occurrence of communication, when the network requests an action
        taken by the application.
            Response: ok if adress is valid
                invalid_param if adress is not valid
        Params:
            appskey:str : 16-byte hexadecimal number representing the application session
        key
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response)= self.send_command(f"mac set appskey {appskey}",
                                timeout=5)
        logging.debug("SET APPSKEY : (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def save_parameters(self):
        """
        Method to save parameters.
            The mac save command must be issued after configuration parameters have been
        appropriately entered from the mac set <cmd> commands. This command will save
        LoRaWAN Class A protocol configuration parameters to the user EEPROM. When the
        next sys reset command is issued, the LoRaWAN Class A protocol configuration will
        be initialized with the last saved parameters.
            The LoRaWAN Class A protocol configuration savable parameters are:
            • band: Band
            • deveui: End-Device Identifier
            • appeui: Application Identifier
            • appkey: Application Key
            • nwkskey: Network Session Key
            • appskey: Application Session Key
            • devaddr: End Device Address
            • ch: All Channel Parameter
                - freq: Frequency
                - dcycle: Duty Cycle
                - drrange: Data Rate Range
                - status: Status
            Response:   ok if address is valid
                        invalid_param if address is not valid
        Params:
        Returns:
                (status_code, response)
                0 - Standard response
                1 - Error
                3 - No response from the module
        """
        response    = []
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command("mac save", timeout=5)
        logging.debug("MAC SAVE: (statuscode,response):%s,%s",status_code,response)

        return (status_code,response)

    def get_datarate(self):
        """
        Method to get the datarate. 
            This command get the current data rate to be used for the next transmission.
        Returns:
                (status_code, datarate)
                0 - Standard response
                3 - No response from the module

                datarate:int : decimal number representing the data rate, from 0 and 7, 
                but within the
                    limits of the data rate range for the defined channels
                    - 0 LoRa: SF12 / 125 kHz 250
                    - 1 LoRa: SF11 / 125 kHz 440
                    - 2 LoRa: SF10 / 125 kHz 980
                    - 3 LoRa: SF9 / 125 kHz 1760
                    - 4 LoRa: SF8 / 125 kHz 3125
                    - 5 LoRa: SF7 / 125 kHz 5470
                invalid_param if address is not valid
        """
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command("mac get dr",timeout=0.2)
        logging.debug("GET DATARATE : (statuscode,datarate):%s,%s",status_code,response)

        if status_code==0:
            response = int(response[0])

        return (status_code,response)

    def get_pwridx(self):
        """
        Method to get the transmission power. 
            This command get the current pwridx rate to be used for the next transmission.
        Returns:
                (status_code, pwr_index)
                0 - Standard response
                3 - No response from the module

                pwr_index:int : 
                decimal number representing the index value for the output power,
                    from 1 to 5 for 868 MHz
                    frequency band.
                    1 - is max
                    5 - is min
                
                Note : In the document it is said that 1 is 14 dBm but I got 20 dBm with a
                device using 5V.
                Also, I've found that :
                    1 Max EIRP         = 14 dBm
                    2 Max EIRP - 2dB   = 12 dBm
                    3 Max EIRP - 4dB   = 10 dBm
                    4 Max EIRP - 6dB   = 8  dBm
                    5 Max EIRP - 8dB   = 6  dBm
            but that was not what we measured. 
                invalid_param if address is not valid
        """
        status_code = 1

        #Send the command
        (status_code,response) = self.send_command("mac get pwridx",timeout=0.2)
        logging.debug("GET PWRIDX : (statuscode,datarate):%s,%s",status_code,response)

        if status_code==0:
            response = int(response[0])

        return (status_code,response)

    def config_savable_parameters_otaa(self,deveui:str,appeui:str,appkey:str,
                            link_check_time_interval:int,
                            channels_and_duty:Dict[int, int]):
        """
        This function will set the savable parameters for over the air activation.
        Call it after any reset.
        Params:
            deveui:str : 8-byte hexadecimal number representing the device EUI
            appeui:str : 8-byte hexadecimal number representing the application EUI
            appkey:str : 16-byte hexadecimal number representing the application key
            link_check_time_interval:int : decimal number that sets the time 
                interval in seconds for the link check process, from 0 to 65535
            channels_and_duty:Dict[int, int] : A dictionnary with :
                key : channel_id:int :  decimal number representing 
                    the channel number, from 0 to 15
                value : dutycycle_percentage:int : percentage representing the duty cycle you want. 
                    If you input 0, the duty cycle will be 100%
            Warning : If a channel is not in the dict key it will be disabled
        Returns:
            (status_code, responses)
                0  - Standard response
                >0 - Number of Error
            Note : we tolerate errors for the channels in case of a bad config
            else we will stop the program
        """
        nb_error  = 0
        responses = []
        #Set deveui
        (status_code,response) = self.set_deveui(deveui)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set deveui")
            return (1,responses)

        #Set appeui
        (status_code,response) = self.set_appeui(appeui)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set appeui")
            return (1,responses)

        #Set appeui
        (status_code,response) = self.set_appkey(appkey)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set appkey")
            return (1,responses)

        #Set link_check_time_interval
        (status_code,response) = self.set_linkchk(link_check_time_interval)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set link check time")
            return (1,responses)

        #Disable all channels
        for channel_id in range(0,3):
            #Disable channel
            (status_code,response) = self.set_channel_status(channel_id,False)
            responses.extend(response)
            if status_code != 0:
                nb_error +=1
                logging.error("Error disabling channel %s",channel_id)

        logging.debug("Now enabling channels")
        #Enable the channels in the dict and set the values
        for key,value in channels_and_duty.items():
            logging.debug("Channel : %s, duty cycle : %s",key,value)
            (status_code,response) = self.set_channel_status(key,True)
            responses.extend(response)
            if status_code != 0:
                nb_error +=1
                logging.error("Error enabling channel %s",key)

            (status_code,response) = self.set_dutycycle(key,value)
            responses.extend(response)
            if status_code != 0:
                nb_error +=1
                logging.error("Error setting duty cycle (%s) for channel %s",value,key)

        #Save the parameters
        (status_code,response) = self.save_parameters()
        responses.extend(response)
        if status_code != 0:
            nb_error +=1
            logging.error("Error saving parameters")

        return (nb_error,responses)

    def config_savable_parameters_abp(self,devaddr:str,nwkskey:str,appskey:str,
                            link_check_time_interval:int,
                            channels_and_duty:Dict[int, int]):
        """
        This function will set the savable parameters for activation by personalization.
        Call it after any reset.
        Params:
            devaddr:str : 4-byte hexadecimal number representing the device address, from
                00000000 – FFFFFFFF
            nwkskey:str : 16-byte hexadecimal number representing the network session key
            appskey:str : 16-byte hexadecimal number representing the application session
            key
            link_check_time_interval:int : decimal number that sets the time 
                interval in seconds for the link check process, from 0 to 65535
            channels_and_duty:Dict[int, int] : A dictionnary with :
                key : channel_id:int :  decimal number representing 
                    the channel number, from 0 to 15
                value : dutycycle_percentage:int : percentage representing the duty cycle you want. 
                    If you input 0, the duty cycle will be 100%
            Warning : If a channel is not in the dict key it will be disabled
        Returns:
            (status_code, responses)
                0  - Standard response
                >0 - Number of Error
            Note : we tolerate errors for the channels in case of a bad config
            else we will stop the program
        """
        nb_error  = 0
        responses = []
        #Set deveui
        (status_code,response) = self.set_dev_addr(devaddr)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set devaddr")
            return (1,responses)

        #Set appeui
        (status_code,response) = self.set_network_session_key(nwkskey)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set appeui")
            return (1,responses)

        #Set appeui
        (status_code,response) = self.set_application_session_key(appskey)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set appkey")
            return (1,responses)

        #Set link_check_time_interval
        (status_code,response) = self.set_linkchk(link_check_time_interval)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set link check time")
            return (1,responses)

        #Disable all channels
        for channel_id in range(0,3):
            #Disable channel
            (status_code,response) = self.set_channel_status(channel_id,False)
            responses.extend(response)
            if status_code != 0:
                nb_error +=1
                logging.error("Error disabling channel %s",channel_id)

        logging.debug("Now enabling channels")
        #Enable the channels in the dict and set the values
        for key,value in channels_and_duty.items():
            logging.debug("Channel : %s, duty cycle : %s",key,value)
            (status_code,response) = self.set_channel_status(key,True)
            responses.extend(response)
            if status_code != 0:
                nb_error +=1
                logging.error("Error enabling channel %s",key)

            (status_code,response) = self.set_dutycycle(key,value)
            responses.extend(response)
            if status_code != 0:
                nb_error +=1
                logging.error("Error setting duty cycle (%s) for channel %s",value,key)

        #Save the parameters
        (status_code,response) = self.save_parameters()
        responses.extend(response)
        if status_code != 0:
            nb_error +=1
            logging.error("Error saving parameters")

        return (nb_error,responses)

    def config_transmission_parameter(self,datarate:int,adr:bool,pwr_index:int):
        """
        This method will set the transmissions parameters.
        Be sure to call config_savable_parameters at least once before this.
        Params:
            datarate:int : decimal number representing the data rate, from 0 and 7, but within the
                limits of the data rate range for the defined channels
                - 0 LoRa: SF12 / 125 kHz 250
                - 1 LoRa: SF11 / 125 kHz 440
                - 2 LoRa: SF10 / 125 kHz 980
                - 3 LoRa: SF9 / 125 kHz 1760
                - 4 LoRa: SF8 / 125 kHz 3125
                - 5 LoRa: SF7 / 125 kHz 5470
            adr_state:bool : If true we set the adr, if not we disable it
            pwr_index:int : 
                decimal number representing the index value for the output power,
                    from 1 to 5 for 868 MHz
                    frequency band.
                    1 - is max
                    5 - is min
                
                Note : In the document it is said that 1 is 14 dBm but I got 20 dBm with a
                device using 5V.
                Also, I've found that :
                    1 Max EIRP         = 14 dBm
                    2 Max EIRP - 2dB   = 12 dBm
                    3 Max EIRP - 4dB   = 10 dBm
                    4 Max EIRP - 6dB   = 8  dBm
                    5 Max EIRP - 8dB   = 6  dBm
            but that was not what we measured. 
        Returns:
            (status_code, responses)
                0 - Standard response
                1 - Error
        """
        responses = []

        #Set the datarate
        (status_code,response) = self.set_datarate(datarate)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set datarate,%s",response)
            return (1,responses)

        #Set the adr
        (status_code,response) = self.set_adr(adr)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set adr %s",response)
            return (1,responses)

        #Set the adr
        (status_code,response) = self.set_pwridx(pwr_index)
        responses.extend(response)
        if status_code != 0 :
            logging.error("Could not set pwridx")
            return (1,responses)

        return (0,responses)

    def join_network(self,abp:bool=False):
        """
        Method to call in order to join the network (OTAA or ABP).
        Please call config_savable_parameters_otaa at least once and 
            config_transmission_parameter before calling this function
        Params:
            abp:bool : If True then it's ABP else it's OTAA
        Returns:
            (status_code, response)
                0 - Standard response
                1 - Error
                3 - Timeout
        """
        response    = []
        status_code = 1

        command = "mac join otaa"
        if abp:
            command = "mac join abp"

        #Send the command
        (status_code,response) = self.send_command(command, timeout=5)
        logging.debug("MAC JOIN : (statuscode,response):%s,%s",status_code,response)
        if status_code != 0 :
            logging.error("Error joining the network")
            return (status_code,response)

        #Now that we've sent the command we should get a response
        start_time = datetime.datetime.now()
        got_response = False
        while not got_response:
            #Check if something is being received
            if self.in_waiting:
                line = self.readline()
                if line !=b'\r\n':
                    #Decode line and remove leading + trailing whitespaces
                    decoded_line = line.decode('utf-8').strip()
                    logging.debug("Decoded line : %s",decoded_line)
                    response.append(decoded_line)
                    got_response = True
            if (datetime.datetime.now() - start_time).seconds > 20:
                status_code=3
                logging.error("Could not join the network")
            time.sleep(0.3)

        logging.debug("decoded line : %s",decoded_line)

        if got_response and 'accepted' in decoded_line:
            status_code = 0
        elif status_code != 3 or 'denied' in decoded_line:
            logging.debug("status code to 1")
            status_code = 1
            logging.error("Could not join the network")

        return (status_code,response)

    def send_uplink(self,data:str,type_confirmed:bool,portno:int=220):
        """
        Method to call to send an uplink.
            You should join the network and set the transmission and network parameters
        first.
            Response: this command may reply with two responses. The first response will be
        received immediately after entering the command. In case the command is valid (ok
        reply received), a second reply will be received after the end of the uplink transmission
            A confirmed message will expect an acknowledgment from the server; otherwise, the
        message will be retransmitted by the number indicated by the command mac set
        retx <value>, whereas an unconfirmed message will not expect any
        acknowledgment back from the server.
        Response after entering the command:
            • ok – if parameters and configurations are valid and the packet was forwarded to
            the radio transceiver for transmission
            • invalid_param – if parameters (<type> <portno> <data>) are not valid
            • not_joined – if the network is not joined
            • no_free_ch – if all channels are busy
            • silent – if the module is in a Silent Immediately state
            • frame_counter_err_rejoin_needed – if the frame counter rolled over
            • busy – if MAC state is not in an Idle state
            • mac_paused – if MAC was paused and not resumed back
            • invalid_data_len if application payload length is greater than the maximum
            application payload length corresponding to the current data rate
        Response after the uplink transmission:
            • mac_tx_ok if uplink transmission was successful and no downlink data was
            received back from the server;
            • mac_rx <portno> <data> if transmission was successful, <portno>: port
            number, from 1 to 223; <data>: hexadecimal value that was received from the
            server;
            • mac_err if transmission was unsuccessful, ACK not received back from the
            server
            • invalid_data_len if application payload length is greater than the maximum
            application payload length corresponding to the current data rate
        Params:
            data:str : Data to send. The length of <data> bytes capable of being
                transmitted are dependent upon the set data rate. 
                (it will be converted to hexadecimal)
                Maximum :
                    51 bytes at SF12 / 125 kHz (lowest data rate)
                    51 bytes at SF11 / 125 kHz
                    51 bytes at SF10 / 125 kHz
                    115 bytes at SF9 / 125 kHz
                    222 bytes at SF8 / 125 kHz
                    222 bytes at SF7 / 125 kHz
            type_confirmed:bool : If true then confirmed message, else unconfirmed
                If a cnf message is sent and is not acknowledged, it will be resend according to
                the value of retx (check set_cnf_retransmissions )
            portno:int : decimal number representing the port number, from 1 to 223 (default 220)
                You are free to use values between 1-223 for any purpose you chose,
                and it is entirely up to you do decide what values your node and infrastructure
                 software sets or looks for and what meaning (if any) it assigns to each value.
        Returns:
            (status_code, response,message)
                0 - Standard response
                1 - Error
                3 - Timeout
            message:str|None : If got mac_rx then message is a string, else None
        """
        #Encode message to hexadecimal
        encoded_data = data.encode("utf-8").hex()

        msg_type = 'uncnf'
        if type_confirmed :
            msg_type = 'cnf'

        command = f"mac tx {msg_type} {portno} {encoded_data}"

        response    = []
        status_code = 1
        message = None

        #Send the command
        (status_code,response) = self.send_command(command, timeout=5)
        logging.debug("MAC TX: (statuscode,response):%s,%s",status_code,response)
        if status_code != 0 :
            logging.error("Error sending uplink")
            return (status_code,response,message)

        #Now that we've sent the command we should get a response
        start_time = datetime.datetime.now()
        got_response = False
        while not got_response:
            #Check if something is being received
            if self.in_waiting:
                line = self.readline()
                if line !=b'\r\n':
                    #Decode line and remove leading + trailing whitespaces
                    decoded_line = line.decode('utf-8').strip()
                    logging.debug("Decoded line : %s",decoded_line)
                    response.append(decoded_line)
                    got_response = True
            if (datetime.datetime.now() - start_time).seconds > 20:
                status_code=3
                logging.error("Could not get a message")
                return (status_code,response,message)
            time.sleep(0.3)

        if 'mac_rx' in decoded_line :
            #Extract the data
            #mac_rx <portno> <data>
            payload=decoded_line.split(" ")[-1]
            payload_bytes = bytes.fromhex(payload)
            decoded_payload = payload_bytes.decode('utf-8')
            logging.debug("Decoded payload : %s",decoded_payload)
            message = decoded_payload

        if got_response or 'mac_tx_ok' in decoded_line or 'mac_rx' in decoded_line:
            status_code = 0
        elif status_code != 3 or 'invalid_data_len' in decoded_line or 'mac_err' in decoded_line:
            status_code = 1
            logging.error("Could not send the uplink")

        return (status_code,response,message)
