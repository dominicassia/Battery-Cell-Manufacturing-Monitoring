import network, time
from machine import Pin, Timer

led = machine.Pin('WL_GPIO0', machine.Pin.OUT) # On-board LED
timer = Timer()

def blink(timer):
    led.toggle()

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while not wlan.isconnected():
        try:
            print('connecting to network...')
            wlan.connect('doma-iphone', 'bruhbruh')
        except OSError:
            time.sleep(2)
    print('connected!\nnetwork config:', wlan.ifconfig())
    
# START
connect_wifi()
timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)