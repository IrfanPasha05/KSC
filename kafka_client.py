import json, os, time
from kafka import KafkaProducer
BROKERS=os.getenv("KAFKA_BOOTSTRAP_SERVERS","kafka:9092")
def publish_order_created(order):
    producer=None
    while producer is None:
        try:
            producer=KafkaProducer(bootstrap_servers=BROKERS.split(","),value_serializer=lambda v: json.dumps(v).encode("utf-8"),acks="all",retries=5,linger_ms=10)
        except Exception as exc:
            print(f"Kafka unavailable: {exc}"); time.sleep(3)
    event={"event_type":"order.created","version":1,"order":order}
    meta=producer.send(os.getenv("KAFKA_TOPIC_ORDER_CREATED","ksc.order.created"),value=event,key=str(order["id"]).encode("utf-8")).get(timeout=15)
    producer.close()
    return {"topic":meta.topic,"partition":meta.partition,"offset":meta.offset}
