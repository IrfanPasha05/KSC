import json
import os
import time

from kafka import KafkaConsumer

from whatsapp import send_order_notification

BROKERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC_ORDER_CREATED", "ksc.order.created")
GROUP = os.getenv("KAFKA_GROUP_ID", "ksc-notification-worker")


def main():
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BROKERS.split(","),
                group_id=GROUP,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            )

            print(f"Listening to {TOPIC} as {GROUP}")

            for message in consumer:
                event = message.value
                print(f"Received order event: {event}")

                try:
                    print(send_order_notification(event))
                except Exception as exc:
                    print(f"Notification failed: {exc}")

            return

        except Exception as exc:
            print(f"Kafka unavailable: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    main()
