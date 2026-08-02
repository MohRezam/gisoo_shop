# """
# Kafka helper
# """
#
# import json
# import logging
#
# from kafka import KafkaProducer
#
# from core_gisoo_backend import settings
# from utils.general.logger import Logger
#
# logger = logging.getLogger("custom")
#
#
# def get_kafka_producer(host, retries=3):
#     """
#     Get kafka producer
#     """
#     if host is None:
#         Logger.error(logger, "kafka host is null", title="kafka")
#         return None
#     try:
#         return KafkaProducer(
#             bootstrap_servers=[host],
#             value_serializer=lambda v: json.dumps(v).encode("utf-8"),
#             retries=retries,
#         )
#     except Exception:
#         Logger.error(logger, "Fail to produce kafka: {e}", title="kafka")
#         return None
#
#
# def create_new_topic(
#     host, name, partition=1, replica_factor=1, client_id="panel-sport-backend"
# ):
#     from kafka import KafkaAdminClient
#     from kafka.admin import NewTopic
#
#     admin = KafkaAdminClient(bootstrap_servers=[host], client_id=client_id)
#     admin.create_topics([NewTopic(name, partition, replica_factor)])
#
#
# def send_kafka(
#     producer: "KafkaProducer",
#     topic: str,
#     data: dict,
#     timeout=settings.PREDICTION_KAFKA_SEND_TIMEOUT,
# ):
#     """
#     Send data to kafka
#     """
#     return producer.send(topic=topic, value=data).get(timeout=timeout)
