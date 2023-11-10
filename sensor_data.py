import json
import random

class SensorDataGenerator:
    def __init__(self):
        self.sensor_data = {
            'sensor1': {
                'location1': {
                    'sublocation1': None,
                    'sublocation2': None,
                },
                'location2': None,
            },
            'sensor2': {
                'location1': {
                    'sublocation1': None,
                    'sublocation2': None,
                },
                'location2': None,
            },
            
        }

        self.generate_dummy_data()

    def generate_dummy_data(self):
        for sensor_type, locations in self.sensor_data.items():
            self._generate_dummy_data_recursive(locations)

    def _generate_dummy_data_recursive(self, node):
        if isinstance(node, dict):
            for key, value in node.items():
                node[key] = self._generate_dummy_data_recursive(value)
        else:

            return random.uniform(0, 100)

    def get_sensor_data(self, data_address=None):
        if data_address:
            address_parts = data_address.split('.')
            current_node = self.sensor_data
            for part in address_parts:
                current_node = current_node.get(part, {})
                if not current_node:
                    break
            return json.dumps({data_address: current_node})
        else:
            return json.dumps(self.sensor_data)


sensor_generator = SensorDataGenerator()
print(sensor_generator.get_sensor_data())  # Get all sensor data
print(sensor_generator.get_sensor_data('sensor1.location1.sublocation1'))  # Get specific sensor da

