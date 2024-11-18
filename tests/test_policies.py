import os
import sys
import unittest


__location__: str = os.path.dirname(os.path.abspath(__file__))
broker_path: str = os.path.join(__location__,
                                 os.pardir,
                                 'cars', 'modules', 'broker', 'module')

if not os.path.exists:
    print('failed to find policies in', broker_path)
    exit(1)
else:
    sys.path.insert(1, broker_path)
    from policies import policies, check_operation


length: int = len(policies)
event_id: int = 0


def next_event(self) -> int:
    global event_id

    event_id += 1
    return event_id


class TestOperation(unittest.TestCase):
    event = next_event

    def test_true(self):
        result = check_operation(self.event(), {
            'source': policies[1]['src'],
            'deliver_to': policies[1]['dst']
        })

        self.assertEqual(result, True)

    def test_false(self):
        result = check_operation(self.event(), {
            'source': 'foo',
            'deliver_to': 'bar'
        })

        self.assertEqual(result, False)

    def test_true2(self):
        result = check_operation(self.event(), {
            'source': policies[2]['src'],
            'deliver_to': policies[2]['dst']
        })

        self.assertEqual(result, True)

    def test_blank(self):
        result = check_operation(self.event(), {
            'source': '',
            'deliver_to': ''
        })

        self.assertEqual(result, False)

    def test_iot_system(self):
        ops = (
            ('conn_with_manag_sys', 'command_validator', True),
            ('eblocks', 'conn_with_manag_sys', True),
            ('park_management_system', 'conn_with_manag_sys', True),
            ('conn_with_manag_sys', 'park_management_system', True),
            ('payment_validator', 'conn_with_manag_sys', True),
            ('conn_with_manag_sys', 'payment_validator', True),
            ('acccess_validator', 'conn_with_manag_sys', True),
            ('conn_with_manag_sys', 'acccess_validator', True),
            ('ic', 'conn_with_manag_sys', True),
            
            ('conn_with_mob_app', 'mobile-client', True),
            ('mobile-client', 'conn_with_mob_app', True),
            ('conn_with_mob_app', 'payment_validator', True),
            ('payment_validator', 'conn_with_mob_app', True),
            ('conn_with_mob_app', 'access_validator', True),
            ('access_validator', 'conn_with_mob_app', True),
            ('conn_with_mob_app', 'command_validator', True),
            ('conn_with_mob_app', 'data_validator', True),

            ('ic', 'doors_controller', True),
            ('doors_controller', 'ic', True),
            ('engine_controller', 'ic', True),
            ('ic', 'engine_controller', True),
            ('data_validator', 'ic', True),
            ('payment_validator', 'ic', True),
            ('access_validator', 'ic', True),
            ('command_validator', 'ic', True),

            ('conn_with_mob_app', 'ic', False),
            ('ic', 'data_validator', False),
            ('conn_with_manag_sys', 'ic', False),
            ('ic', 'access_validator', False),
            ('ic', 'payment_validator', False),
        )
        for op in ops:
            result = check_operation(self.event(), {
                'source': op[0],
                'deliver_to': op[1]
            })

            self.assertEqual(result, op[2])

    def test_technical_status_module(self):
        ops = (
            ('tire_sensons', 'eblocks', True),
            ('vehicle_braking', 'eblocks', True),
            ('fuel_tank', 'eblocks', True),
            ('headlights', 'eblocks', True),
            
            ('eblocks', 'fuel_tank', False),
            ('eblocks', 'tire_sensons', False),
            ('eblocks', 'vehicle_braking', False),
            ('eblocks', 'headlights', False),
        )

        for op in ops:
            result = check_operation(self.event(), {
                'source': op[0],
                'deliver_to': op[1]
            })

            self.assertEqual(result, op[2])

    def test_engine_module(self):
        ops = (
            ('engine', 'engine_controller', True),
            ('engine_controller', 'eblocks', True),

            ('engine_controller', 'engine', False),
            ('eblocks', 'engine', False),
        )

        for op in ops:
            result = check_operation(self.event(), {
                'source': op[0],
                'deliver_to': op[1]
            })

            self.assertEqual(result, op[2])

    def test_navigation_module(self):
        ops = (
            ('gps', 'navigation_handler', True),
            ('navigation_handler', 'eblocks', True),

            ('navigation_handler', 'gps', False),
            ('eblocks', 'gps', False),
        )

        for op in ops:
            result = check_operation(self.event(), {
                'source': op[0],
                'deliver_to': op[1]
            })

            self.assertEqual(result, op[2])

    def test_doors_module(self):
        ops = (
            ('doors_controller', 'locking_device', True),
            ('doors_controller', 'eblocks', True),

            ('locking_device', 'eblocks', False),
            ('locking_device', 'doors_controller', False),
        )

        for op in ops:
            result = check_operation(self.event(), {
                'source': op[0],
                'deliver_to': op[1]
            })

            self.assertEqual(result, op[2])

    def test_validation_module(self):
        ops = (
            ('eblocks', 'data_validator', True),
            ('command_validator', 'payment_validator', True),
            ('command_validator', 'access_validator', True),
           
            ('eblocks', 'payment_validator', False),
            ('payment_validator', 'eblocks', False),
            ('command_validator', 'eblocks', False),
            ('data_validator', 'eblocks', False),
        )

        for op in ops:
            result = check_operation(self.event(), {
                'source': op[0],
                'deliver_to': op[1]
            })

            self.assertEqual(result, op[2])


if __name__ == '__main__':
    unittest.main(verbosity=2)
