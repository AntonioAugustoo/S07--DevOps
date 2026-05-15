
import paho.mqtt.publish as publish

mensagem = "🔔 Nova proposta de troca para você!"
topic = "trocas/123/notificacoes"

publish.single(
    topic,
    payload=mensagem,
    hostname="test.mosquitto.org",
    port=1883
)

print(f"📤 [Enviado] {mensagem} para tópico {topic}")
