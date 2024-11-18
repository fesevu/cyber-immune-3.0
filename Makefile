SHELL := bash

MODULES := access_validator \
			command_validator \
			conn_with_manag_sys \
			conn_with_mob_app \
			data_validator \
			doors_controller \
			eblocks \
			engine \
			engine_controller \
			fuel_tank \
			gps \
			headlights \
			ic \
			locking_device \
			navigation_handler \
			payment_validator \
			tire_sensors \
			vehicle_braking \
			payment-system \
			management-system \
			mobile-client \


SLEEP_TIME := 10

dev_install:
	sudo apt install librdkafka-dev python3-venv
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -U pip
	.venv/bin/pip install -r requirements.txt

remove_kafka:
	if docker stop zookeeper broker; then \
		docker rm zookeeper broker; \
	fi
all:
	make remove_kafka
	docker compose down
	docker compose up --build -d
	sleep ${SLEEP_TIME}

	for MODULE in ${MODULES}; do \
		echo Creating $${MODULE} topic; \
		docker exec broker \
			kafka-topics --create --if-not-exists \
			--topic $${MODULE} \
			--bootstrap-server localhost:9092 \
			--replication-factor 1 \
			--partitions 1; \
	done

logs:
	docker compose logs -f --tail 100
	
test:
	make all
	sleep ${SLEEP_TIME}
	python3 -m pytest tests/e2e-test/test_base_scheme.py
	make clean

test_security:
	python3 tests/test_policies.py

clean:
	docker compose down 
	for MODULE in ${MODULES}; do \
		docker rmi $${MODULE};  \
	done
