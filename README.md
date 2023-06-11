# OpenPV
Comprehensive photovoltaics system (600 W) with battery based energy spreading, control and visualization.

The complete system consists of the following subsystems:
* 600 W photovoltaic system: two 400 W panels, one Hoymiles HM-600 inverter
* [OpenDTU](https://github.com/tbnobody/OpenDTU): Really awesome ESP32 based WiFi frontend for the HM-600
* Volkszaehler SmartMeter EHZ: Another awesome ESP8266 Wifi frontend to gather energy information from an EHZ energy meter via its infrared interface
* Battery extension of the PV system: Two Victron SmartSolar and two Renogy 24 V / 25 Ah batteries for spreading the daytime solar energy over night
* Optimizing the energy spreading: Dockerized Python script optimzes the battery energy spreading for base-load operation
* Data logging and visualization: Dockerized MQTT data brokerage and Grafana visualization with the support of InfluxDB and Telegraf
