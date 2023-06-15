# OpenPV Overview
Comprehensive photovoltaics system (600 W) with battery based energy spreading, control and visualization.

The complete system consists of the following subsystems:
1. 600 W photovoltaic system: two 400 W panels, one Hoymiles HM-600 inverter
2. [OpenDTU](https://github.com/tbnobody/OpenDTU): Really awesome ESP32 based WiFi frontend for the HM-600
3. Volkszaehler SmartMeter EHZ: Another awesome ESP8266 Wifi frontend to gather energy information from an EHZ energy meter via its infrared interface
4. Data logging and visualization: Dockerized MQTT data brokerage and Grafana visualization with the support of InfluxDB and Telegraf
5. Battery extension of the PV system: Two Victron SmartSolar and two Renogy 24 V / 25 Ah batteries for spreading the daytime solar energy over night
6. Optimizing PV yield by energy spreading: Dockerized Python script optimizes the yield by battery energy spreading targeting basic load coverage

I started step by step with 1. - 4. and then decided to extend the little photovoltaic system by batteries (5.) and programmed a python script for optimizing (6.).

# The basic PV system
* Two monocristalline solar panels [TrinaSolar VertexS TSM-405 DE09.08](https://github.com/s-t-e-f-a-n/OpenPV/files/11762367/DE_Datasheet_VertexS_DE09.08_2021_A.pdf)

<img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/ec4fbf72-5db7-4878-a9c1-0756b01ddf20" width="200"> <img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/a43ccae1-1bdb-40c9-b6c3-b0774fd46b0c" width="200"> <img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/8b546799-029f-473c-a256-9b3ac4a9e6fb" width="200" height="270"> <img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/cf318696-577b-4477-92cd-d15f95446e9c" width="200"> 

* One dual-DC/single AC 600 W inverter [Hoymiles HM-600](https://github.com/s-t-e-f-a-n/OpenPV/files/11762369/hm600.pdf)
<img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/3231166a-8a3b-495a-b62a-e01aefce2be1" width="200">

I mounted some bracket stands 

# OpenDTU
As the Hoymiles HM-600 inverter is not equipped with a general WiFi interfacee but instead with a proprietrary wireless interface you'd need for remote access to the inverter a so called Data Transer Unit (DTU) from Hoymiles which you'd get on the market for appr. 50 € - 100 €. It only works via a Hoymiles server where you'd have to register etc.

Contrary to the commercial solution there are two open source solutions available which cost you ca. 30 €:
* [Ahoy-DTU](https://github.com/lumapu/ahoy)
* [OpenDTU](https://github.com/tbnobody/OpenDTU)

A really good comparison of both projects (...sorry, German ;-) https://blog.helmutkarger.de/balkonkraftwerk-teil-8-opendtu-und-ahoydtu-fuer-hoymiles-wechselrichter/
Both projects are really awesome. The story of development reads quite exciting [here](https://www.mikrocontroller.net/topic/525778).

However, I decided for OpenDTU and followed the instructions on [OpenDTU](https://github.com/tbnobody/OpenDTU) and ordered four basic components:
* NodeMCU-ESP32 Development Board @ 11 €
* nRF24L01+ Wireless Transceiver Module  @ 2 €
* 100-240 VAC to 5 VDC / 600 mA converter @ 9 €
* ABS Housing 83x58x33 mm @ 10 € 
* breadboard, cable, solder tin @ ca. 5 €

<img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/29769f5b-adfd-4b61-9e83-b76f14064ce6" width="200">  <img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/306e99b0-a73d-43a7-8eed-3995c031e3c5" width="200"> <img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/2a5e95b4-65b7-4e06-bb9f-71698c63c742" width="200"> <img src="https://github.com/s-t-e-f-a-n/OpenPV/assets/16215726/b9317b2c-ed11-4398-8279-7dabd766023f" width="200">

