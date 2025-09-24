import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

from aliyun.log import LogClient
from confluent_kafka import Producer


load_dotenv()  # load .env into os.environ

# ================= CONFIG =================
# SLS config
ENDPOINT = os.environ.get("ENDPOINT")  # replace with your SLS endpoint
ACCESS_KEY_ID = os.environ.get("ACCESS_KEY_ID")
ACCESS_KEY_SECRET = os.environ.get("ACCESS_KEY_SECRET")
PROJECT = os.environ.get("PROJECT")
LOGSTORE = os.environ.get("LOGSTORE")

# Kafka config
KAFKA_BROKERS = os.environ.get("KAFKA_BROKERS")  # comma-separated list
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")

# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Init clients
log_client = LogClient(ENDPOINT, ACCESS_KEY_ID, ACCESS_KEY_SECRET)
producer = Producer({"bootstrap.servers": KAFKA_BROKERS})


def delivery_report(err, msg):
    """Kafka delivery callback (async)"""
    if err is not None:
        logging.error(f"Delivery failed: {err}")
    else:
        logging.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def handle_shard(shard_id: int):
    logging.info(f"Worker started for shard {shard_id}")
    # start from the earliest logs
    cursor = log_client.get_begin_cursor(PROJECT, LOGSTORE, shard_id).cursor

    while True:
        try:
            res = log_client.pull_logs(PROJECT, LOGSTORE, shard_id, cursor, 100)
            cursor = res.get_next_cursor()

            logs = res.get_loggroup_json_list()
            if not logs:
                time.sleep(1)
                continue

            for log_group in logs:
                msg = json.dumps(log_group)
                producer.produce(
                    KAFKA_TOPIC,
                    value=msg.encode("utf-8"),
                    callback=delivery_report
                                    )

            producer.poll(0)
            logging.info(f"Shard {shard_id}: sent {len(logs)} log groups to Kafka")

        except Exception as e:
            logging.error(f"Error in shard {shard_id}: {e}")
            time.sleep(2)

def main():
    # discover shards
    shards = log_client.list_shards(PROJECT, LOGSTORE).shards
    shard_ids = [s["shardID"] for s in shards]
    logging.info(f"Starting workers for shards: {shard_ids}")

    with ThreadPoolExecutor(max_workers=len(shard_ids)) as executor:
        for sid in shard_ids:
            executor.submit(handle_shard, sid)

        # keep main alive
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            logging.info("Stopping workers...")
            producer.flush()


if __name__ == "__main__":
    main()