import os
import json
import threading

from uuid import uuid4
from confluent_kafka import Consumer, OFFSET_BEGINNING

from .producer import proceed_to_deliver


MODULE_NAME: str = os.getenv("MODULE_NAME")


def send_to_ic(id, details):
    details['deliver_to'] = 'ic'
    details['operation'] = 'data_validation_result'
    proceed_to_deliver(id, details)

def send_to_manager_system(id, details):
    details['deliver_to'] = 'conn_with_manag_sys'
    details['operation'] = 'validate_from_manag_sys'
    proceed_to_deliver(id, details)


def send_to_mob_app(id, details):
    details['deliver_to'] = 'conn_with_mob_app'
    details['operation'] = 'validate_from_mob_app'
    proceed_to_deliver(id, details)


def handle_event(id, details_str):
    """ Обработчик входящих в модуль задач. """
    details = json.loads(details_str)

    source: str = details.get("source")
    deliver_to: str = details.get("deliver_to")
    operation: str = details.get("operation")

    print(f"[info] handling event {id}, "
          f"{source}->{deliver_to}: {operation}")

    if operation == "access_validation":
        print(f"По запросу: {id}. Происходит валидация доступа: {details['data']}")
        
        # запрашиваем проверку у мобильного ПО
        send_to_mob_app(id, details)

        # запрашиваем проверку у менеджера
        send_to_manager_system(id, details)
        
    elif operation in (
        'validation_response_from_mob_app',
        'validation_response_from_manag_sys'
    ):
        send_to_ic(id, details)


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