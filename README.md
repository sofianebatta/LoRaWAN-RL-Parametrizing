# LoRaWAN RL Parametrizing

In this work, we propose the integration of reinforcement learning (Q-learning) for decentralized and adaptive resource allocation in LoRaWAN networks. The approach enables end devices to autonomously configure their transmission parameters, such as spreading factors and power levels, based on local environmental feedback. The model design carries a distributed and adaptive plug-and-play model that enables end Lora devices to operate autonomously without impacting the overall algorithm performance.

# Model Training
The spreading power (SF) and transmitting power (TP) allocation learning process is illustrated in the following figure. 

![Phase2](https://github.com/user-attachments/assets/c57e8d90-b2d8-4134-b4b5-44197bdf626c)


During the model conception, various reward formulations were investigated to optimize the performances of our model. This later specifically promotes the following behaviors:

* **TP optimization**: Positive rewards are given for actions that optimize TP while preserving a stable communication link. i.e, actions that reduce TP while staying within the required SNR thresholds (Table I) receive higher rewards.
* **Maintaining communication QoS**: Positive rewards are granted when actions maintain or increase SNR values above the necessary reception thresholds (Table I), ensuring a consistently high communication QoS.
* **Penalties for SNR declines**: Negative rewards are assigned for actions resulting in SNR values that exceed limits or fail to meet required margins. Similarly, actions that increase energy consumption without enhancing SNR margins incur penalties to discourage resources waste.

|SF | Data rate [kb/s] |Sensitivity [dBm] |Required SNR [dB]|
|---|---|----|-------|
7 | 5.458 | -126.5 | -7.5|
8 | 3.125 | -127.25 | -10|
9 | 1.757 | -131.25 | -12.5|
10 | 0.976 | -132.75 | -15|
11 | 0.537 | -133.25 | -17.5|
12 | 0.293 | -134.5 | -20|


# Experimental Setup

To validate the designed solution for LoRaWAN SF and TP Parametrizing, we implemented a real testbed deployed within Toulouse University campus (as shown in the following map). For the backend setup, we used [Mosquitto](https://mosquitto.org/). 

![carte_experimentation](https://github.com/user-attachments/assets/94fcb6dd-1791-482a-9ec3-9c716798ec59)

The implemented network consists of 3 Gateways and multiple Raspberry Pi4 model B EDs equiped with LoRa microchip-based RN2483 (illustrated in Fig. 4). The experimentation sources code is provided in this repository.

![IMG_20250203_103702](https://github.com/user-attachments/assets/636d4cfe-e1da-4744-90ff-163a4672a23b)

![RN2483_picture](https://github.com/user-attachments/assets/72141cbf-0146-4ff7-9adb-195b2c987d9a)


# Scientific Article Citation
Comming soon!

### Authors: 
  * M. S. BATTA (mohamed-sofiane.batta@irit.fr)
  * R. KACIMI (rahim.kacimi@irit.fr)
  * A. MORAL (alexandre.moral@irit.fr)
  



