
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado ao broker com status", rc)
    client.subscribe("trocas/123/notificacoes")

def on_message(client, userdata, msg):
    print(f"📥 [Notificação recebida] {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)
client.loop_forever()
