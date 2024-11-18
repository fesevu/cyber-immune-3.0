import os
import json
import threading

from uuid import uuid4
from confluent_kafka import Consumer, OFFSET_BEGINNING

from .producer import proceed_to_deliver
import time

MODULE_NAME: str = os.getenv("MODULE_NAME")


car_information = []


def send_to_command_validation(id, details):
    details['operation'] = 'command_validation'
    proceed_to_deliver(id, details)


def send_to_data_validator(id, info):
    proceed_to_deliver(id, json.dumps(dict(
        source=MODULE_NAME,
        deliver_to="data_validator",
        operation="data_validation",
        data=info
    )))


def send_to_headlights(id):
    proceed_to_deliver(id, json.dumps(dict(
        source=MODULE_NAME,
        deliver_to="headlights",
        operation="send_current_headlights_state",
        data={}
    )))


def send_to_fuel_tank(id):
    proceed_to_deliver(id, json.dumps(dict(
        source=MODULE_NAME,
        deliver_to="fuel_tank",
        operation="send_current_fuel_tank_state",
        data={}
    )))


def send_to_manager_system(id, details):
    details['deliver_to'] = 'conn_with_manag_sys_response'
    proceed_to_deliver(id, details)


def send_to_mobile_app(id, details):
    details['deliver_to'] = 'conn_with_mob_app_response'
    proceed_to_deliver(id, details)


def handle_event(id, details_str):
    """ Обработчик входящих в модуль задач. """
    details = json.loads(details_str)

    source: str = details.get("source")
    deliver_to: str = details.get("deliver_to")
    operation: str = details.get("operation")

    print(f"[info] handling event {id}, "
          f"{source}->{deliver_to}: {operation}")
    
    send_to_headlights(uuid4)
    send_to_fuel_tank(uuid4)

    if operation == 'lock_car_doors_result':
        car_information.append(details.get('data'))
    
    elif operation == 'send_current_engine_state':
        car_information.append(details.get('data'))
    
    elif operation == 'send_current_fuel_tank_state':
        car_information.append(details.get('data'))
    
    elif operation == 'send_current_headlights_state':
        car_information.append(details.get('data'))
    
    elif operation == 'send_current_gps_data':
        car_information.append(details.get('data'))
    
    elif operation == 'send_current_tire_sensors_state':
        car_information.append(details.get('data'))
    
    elif operation == 'send_current_vehicle_braking_state':
        car_information.append(details.get('data'))
    
    send_to_data_validator(uuid4(), car_information)

    if operation == 'conn_with_manag_sys_request':
        print("Получили запрос от менеджера")
        send_to_command_validation(id, details)
        time.sleep(50)
        send_to_manager_system(id, details)

    elif operation == 'conn_with_mob_app_request':
        print("Получили запрос от мобильного приложения")
        send_to_command_validation(id, details)
        time.sleep(50)
        send_to_mobile_app(id, details)


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