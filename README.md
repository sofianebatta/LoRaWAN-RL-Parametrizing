**LoRaWAN RLParametrizing**

In this work, we propose the integration of reinforcement learning (Q-learning) for decentralized and adaptive resource allocation. The approach enables end devices to autonomously configure their transmission parameters, such as spreading factors and power levels, based on local environmental feedback. The model design carries a distributed and adaptive plug-and-play model that enables end Lora devices to operate autonomously without impacting the overall algorithm performance.

**Model Training**
The spreading power and transmitting power allocation learning process is illustrated in the following figure. 

![Phase2](https://github.com/user-attachments/assets/c57e8d90-b2d8-4134-b4b5-44197bdf626c)


During the model conception, various reward formulations were investigated to optimize the performances of our model. This later specifically promotes the following behaviors:

TP optimization: Positive rewards are given for actions that optimize TP while preserving a stable communication link. i.e, actions that reduce TP while staying within the required SNR thresholds (Table II) receive higher rewards.
Maintaining communication QoS: Positive rewards are granted when actions maintain or increase SNR values above the necessary reception thresholds (Table II), ensuring a consistently high communication QoS.
Penalties for SNR declines: Negative rewards are assigned for actions resulting in SNR values that exceed limits or fail to meet required margins. Similarly, actions that increase energy consumption without enhancing SNR margins incur penalties to discourage resources waste.

The provided code is adapted to the LoRa microchip-based RN2483
