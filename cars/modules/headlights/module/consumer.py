import os
import json
import threading

from uuid import uuid4
import time
import random
from confluent_kafka import Consumer, OFFSET_BEGINNING

from .producer import proceed_to_deliver


MODULE_NAME: str = os.getenv("MODULE_NAME")


def send_to_eblocks(id, details):
    details["deliver_to"] = "eblocks"
    proceed_to_deliver(id, details)


def handle_event(id, details_str):
    """ Обработчик входящих в модуль задач. """
    details = json.loads(details_str)

    source: str = details.get("source")
    deliver_to: str = details.get("deliver_to")
    operation: str = details.get("operation")

    print(f"[info] handling event {id}, "
          f"{source}->{deliver_to}: {operation}")

    if operation == "send_current_headlights_state":
        send_to_eblocks(id, details)


def consumer_job(args, config):
    consumer = Consumer(config)

    def reset_offset(verifier_consumer, partitions):
        if not args.reset:
            return

        for p in partitions:
            p.offset = OFFSET_BEGINNING
        verifier_consumer.assign(partitions)

    topic = MODULE_NAME
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            if random.randint(0,1):
                time.sleep(45)
                handle_event(uuid4(), json.dumps(dict(
                    source=MODULE_NAME,
                    deliver_to="eblocks",
                    operation="send_current_headlights_state",
                    data={
                        "is_left_working": bool(random.randint(0,1)),
                        "is_right_working": bool(random.randint(0,1)),
                        "exactly": bool(random.randint(0,1)),
                    }
                )))

            msg = consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    handle_event(id, details_str)
                except Exception as e:
                    print(f"[error] Malformed event received from " \
                          f"topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()

def start_consumer(args, config):
    print(f'{MODULE_NAME}_consumer started')
    threading.Thread(target=lambda: consumer_job(args, config)).start()