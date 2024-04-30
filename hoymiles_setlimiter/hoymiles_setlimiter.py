# !/usr/bin/python
# -*- coding: utf-8 -*-
# Thanks to https://github.com/tbnobody/OpenDTU
# ...further thanks to https://gitlab.com/p3605/hoymiles-tarnkappe
# 
# Das Script ermittelt den aktuellen Leistungsbezug aus dem Stromnetz am Stromzähler 
# und setzt ihn mit dem aktuell gesetzten (alten) Leistungslimit des Wechselrichters ins Verhältnis.
# Das neue Limit ist die Summe aus Leistungsbezug und (altem) Leistungslimit.
# Das neue Leistungslimit wird nach oben auf das Maximum und nach unten auf das Minimum des Wechselrichters begrenzt.

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from pytz import timezone
from astral import LocationInfo
from astral.sun import sun
from astral.sun import elevation
import sys

########## begin of individual parameters #########################

# Seriennummern des Hoymiles Wechselrichters
serial = "114182940914"
# Maximale Leistung des Wechselrichters
maximum_wr = 600
# Minimale Leistung des Wechselrichters
minimum_wr = 85
# Ziel der Hauseinspeisung (bspw. 10 bedeutet, dass 10 Watt Verbrauch aus Stromnetz avisiert wird)
target_power = 0
# geo location
latitude = 52.4300994387164
longitude = 13.2885230408758
# Position of sun from Astral lib
city = LocationInfo("Berlin","Germany","Europe/Berlin",latitude,longitude)
tz = timezone('Europe/Berlin')
e_max = 60 # maximum elevation at location

# MQTT Server
server = "solg.fritz.box"
port = 1883

# mqtt-strings zum lesen und schreiben zusammensetzen
do_restart = "solar/"+serial+"/cmd/restart"                     # Restart Inverter for resetting yield.day
set_limit = "solar/"+serial+"/cmd/limit_nonpersistent_absolute" # Leistungslimit Wechselrichter setzen
akt_power = "solar/"+serial+"/0/power"                          # Status aktuelle AC-Leistungslieferung vom Wechselrichter
limit_alt = "solar/"+serial+"/status/limit_absolute"            # Status aktuelles Leistungslimit Wechselrichter
akt_reachable = "solar/"+serial+"/status/reachable"             # Status Erreichbarkeit Wechselrichtrer
akt_producing = "solar/"+serial+"/status/producing"             # Status Leistungslieferung Wechselrichter
akt_wirkleistung = "stromzaehler/tele/SENSOR"                   # Topic zum json-Feld der aktuellen Leistung am Hauszähler

########## end of individual parameters #########################

# variables for processing
grid_sum = 0     # local value of grid power consumption (+) / provision (-) from MQTT/Tasmota
reachable = 0    # local reachable-flag from MQTT/DTU
producing = 0    # local producing-flag from MQTT/DTU
power = 0        # local AC power of Hoymiles from MQTT/DTU
old_limit = 0    # local current/old limit from MQTT/DTU
new_limit = 0    # new limit to be set to MQTT/DTU
state = 0        # collects "got-"flags
restart = 0	 # flag for restart Hoymiles

# "got"flags to signal MQTT value reception
got_reachable = 0x01
got_producing = 0x02
got_grid = 0x04
got_olimit = 0x08
got_power = 0x10

# reception of general MQTT message
def on_message(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
#    print("on_message",message_received)
#    print("Topic: ", message.topic)

# reception of reachable MQTT message
def on_message_reachable(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global reachable, got_reachable, state
    reachable = int(float(message_received))
    if reachable:
        state |= got_reachable
    else:
        reachable = 0

# reception of producing MQTT message
def on_message_producing(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global producing, got_producing, state
    if reachable:
        producing = int(float(message_received))
        state |= got_producing

# reception of Hoymiles/DTU AC power MQTT message
def on_message_power(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global power, got_power, state
    if reachable:
        power = int(float(message_received))
        state |= got_power

# reception of current/old limit MQTT message
def on_message_old_limit(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global old_limit, got_olimit, state
    if reachable:
        old_limit = int(float(message_received))
        state |= got_olimit
        if old_limit >= maximum_wr:
            old_limit = maximum_wr

# reception of grid power MQTT message
def on_message_hausleistung(client, userdata, message):
    json_tree = json.loads(message.payload.decode("utf-8"))
    global grid_sum, got_grid, state
    grid_sum = json_tree["eHZ"]["wirkleistung"]
    state |= got_grid

# connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print(datetime.now(),"MQTT broker connection ok")
    else:
        print(datetime.now(),"MQTT broker returned code=",rc)
        sys.exit(0)

# disconnection from MQTT broker
def on_disconnect(client, userdata, rc):
    client.connected_flag=False #unset flag
    print(datetime.now(),"MQTT broker disconnected...reconnection ongoing...")

#
# Main processing starts here
#
# connect to broker
mqtt.Client.connected_flag=False  #create flag in class
client = mqtt.Client()
client.connect(server,port)

# prepare MQTT callbacks
client.message_callback_add(akt_reachable, on_message_reachable)
client.message_callback_add(akt_producing, on_message_producing)
client.message_callback_add(akt_power, on_message_power)
client.message_callback_add(limit_alt, on_message_old_limit)
client.message_callback_add(akt_wirkleistung, on_message_hausleistung)
client.on_message = on_message
client.on_connect = on_connect
client.subscribe([('solar/'+serial+'/#', 0), (set_limit, 0), ('stromzaehler/tele/SENSOR/#', 0)])
client.loop_start()

# not used
#s = sun(city.observer, tz.localize(datetime.now()))
#sunrise = datetime.strptime(f'{s["sunrise"]}'[0:16], "%Y-%m-%d %H:%M")
#sunset = datetime.strptime(f'{s["sunset"]}'[0:16], "%Y-%m-%d %H:%M")

# Forever processing loop
while True:

    # set maximum limit with reference to the sun elevation
    e = max(0, elevation(city.observer, tz.localize(datetime.now())))   # get sun elevation degree (Berlin maximum is ca. 60°) floor limited to zero
    max_limit=(e/e_max)*(e/e_max)*maximum_wr     # at maximum elevation the maximum hoymiles power is set, lower values are weighted quadratic antiproportional
    if (max_limit) < minimum_wr:
        max_limit = minimum_wr

    # restart inverter short after midnight to reset yield.day
    now = 100*datetime.now().time().hour+datetime.now().time().minute
    if now < 5 and got_reachable and not restart:
        restart = 1
        print(datetime.now(),"Restarting Inverter!")
        client.publish(do_restart,1)
    elif now >= 5:
        restart = 0

    time.sleep(30)  # collect MQTT data during this sleep time

    if state == got_grid|got_olimit|got_power|got_producing|got_reachable:
        new_limit = grid_sum + old_limit - target_power
        print(datetime.now(),end="")
        # limit to max limit
        if (new_limit > max_limit):
            new_limit = max_limit
            print(" Set Ceil New Limit: ",new_limit," W / Old Limit",old_limit," W / Max Limit: ",max_limit," W / Grid:",grid_sum," W / Hoy Out: ",power," W ")
        # limit to low limit
        elif new_limit < minimum_wr:
            new_limit = minimum_wr
            print(" Set Floor New Limit: ",new_limit," W / Old Limit",old_limit," W / Max Limit: ",max_limit," W / Grid:",grid_sum," W / Hoy Out: ",power," W ")
        else:
            print(" Set Ctrld New Limit: ",new_limit," W / Old Limit",old_limit," W / Max Limit: ",max_limit," W / Grid:",grid_sum," W / Hoy Out: ",power," W ")
        # send new limit to hoymiles inverter
        client.publish(set_limit,new_limit)
    # for safety set to low limit when MQTT publishes no grid power value
    elif not (state & got_grid) and (state & got_reachable):
        new_limit = minimum_wr
        print(datetime.now(),"Set Floor New Limit: MQTT provides no Mains value!")
        client.publish(set_limit,new_limit)
    else:
        new_limit = minimum_wr
        print(datetime.now(),"MQTT",end="")
        if not (state & got_reachable):
            print("...no Hoy Reachable",end="")
        if not (state & got_producing):
            print("...no Hoy Producing",end="")
        if not (state & got_power):
            print("...no Hoy Power",end="")
        if not (state & got_olimit):
            print("...no Hoy Limit",end="")
        if not (state & got_grid):
            print("...no Grid Power",end="")
        if not client.connected_flag:
            print("...no Broker connection",end="")
        if not reachable:
            reachable = 0
            producing = 0
            power = 0
            old_limit = 0
            print("...RESET Hoy local values",end="")
        print("\r")
    state = 0   # reset MQTT value status

# End
