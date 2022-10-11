# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python

from mqtt-paho import client as mqtt_client

broker = ''
port = ''
topic = ''

client_id = ''
username = ''
password = ''

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
    
def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()