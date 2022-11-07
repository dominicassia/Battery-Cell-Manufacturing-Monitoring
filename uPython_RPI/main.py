# RPI Pico W Pinout reference: https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#pinout-and-design-files-2

# Imports
import network, time
from machine import Pin, Timer
#from hx711_gpio import hx711 # from file import object
from mqtt import MQTTClient

#######################################

SSID = 'netis_3AACDE'
PASS = 'password'

#######################################

mqtt_server = '192.168.1.4' # Broker
client_id = 'rpi_pico'
topic_pub = b'prj3c_test' # Topic

# Create MQTT client object
client = MQTTClient(client_id, mqtt_server, keepalive=3600)

#######################################

# Mosquitto broker config file (mosquitto.conf)
## Create lan listener on laptop
### listener 1883 192.168.1.13
## Allow no authentication
### allow_anonymous true

# Launch broker
## mosquitto -v -c mosquitto.conf
# Launch subscriber
## mosquitto_sub -v -h '192.168.1.13' -t 'prj3c_test'

#######################################

# LED
led = machine.Pin('WL_GPIO0', machine.Pin.OUT) # On-board LED
timer = Timer()

#######################################

def blink(timer):
    led.toggle()

def connect_wifi():    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while not wlan.isconnected():
        try:
            print('connecting to network...')
            wlan.connect(SSID, PASS)
            time.sleep(2)
        except OSError:
            pass
        print('failed to connect to the network. reattempting...')
        time.sleep(10)
    print('connected to wireless:', wlan.ifconfig(), '\n')

def connect_broker():
    try:
        print('connecting to broker...')
        client.connect()
        print('connected to broker', mqtt_server, '\n')
        time.sleep(2)
    
    except OSError:
        print('failed to connect to the broker. reconnecting...')
        time.sleep(5)
        connect_broker()
        
def load_cell():
    # Initialize / 
    #factor = 1 / 1 # factor = read weight / known weight?
    #hx711.set_scale(factor)
    #hx711.tare()
    while True:
        value = hx711.read()
        print(value)
        time.sleep(5)
    

####################################### 
# Start
####################################### 

# Connect
connect_wifi()
connect_broker()

# Begin LED blink
timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink) 

# ADC1 / GP27
load_cell = machine.ADC(27)

# 3.3V = 66lbs
conversion = (100 / 65535)
while True:
    raw_data = load_cell.read_u16()
    
    converted_data = raw_data * conversion
    
    data = bytes(str(converted_data), 'utf-8')
    
    print('Sending: ', data, raw_data)
    
    client.publish(topic_pub, data)
    
    print('sent.')
    time.sleep(2)
