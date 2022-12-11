import network, time
from machine import Pin

LED = Pin(25, Pin.OUT)

def do_blink():
    while True:
        LED.on()
        time.sleep(1)
        LED.off()
        time.sleep(1)
        
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    try:
        print('connecting to network...')
        wlan.connect('', '')
    
    except OSError:
        time.sleep(2)
        
        while not wlan.isconnected():
            print('connecting to network...')
            wlan.connect('', '')
            time.sleep(2)
        
    print('connected!\n network config:', wlan.ifconfig())
    do_blink()
    
# START
do_connect()