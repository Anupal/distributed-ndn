import json
import random
import faker

class MedicalSensorSystem:
    def __init__(self):
        # Initialize the sensor data dictionary with fake patient data
        self.sensor_data = {
            'PatientInfo': self.generate_fake_patient_data(),
            'HeartRate': {
                'ECG': random.randint(60, 100),
                'PPG': random.randint(60, 100),
            },
            'BloodPressure': {
                'Invasive': {
                    'mmHg': random.randint(90, 140),
                    'kPa': self.mmHg_to_kPa(random.randint(90, 140)),
                },
                'NonInvasive': {
                    'mmHg': random.randint(90, 140),
                    'kPa': self.mmHg_to_kPa(random.randint(90, 140)),
                },
            },
            'Glucose': random.uniform(70, 150),
            'Temperature': {
                'Celsius': random.uniform(36.0, 38.0),
                'Fahrenheit': random.uniform(96.8, 100.4),
            },
            'OxygenSaturation': {
                'Percentage': random.uniform(95, 100),
                'Fractional': self.percentage_to_fractional(random.uniform(95, 100)),
            },
            'RespiratoryRate': random.randint(12, 20),
            'Movement': {
                'Accelerometer': {
                    'X': random.uniform(-1, 1),
                    'Y': random.uniform(-1, 1),
                    'Z': random.uniform(-1, 1),
                },
                'Gyroscope': {
                    'Roll': random.uniform(-180, 180),
                    'Pitch': random.uniform(-90, 90),
                    'Yaw': random.uniform(-180, 180),
                },
            },
            'EEG': random.uniform(0, 100),
        }

    def generate_fake_patient_data(self):
        # Generate fake patient data using the Faker library
        fake = faker.Faker()
        return {
            'PatientID': fake.uuid4(),
            'FirstName': fake.first_name(),
            'LastName': fake.last_name(),
            'Age': fake.random_int(min=18, max=99),
            'Gender': fake.random_element(elements=('Male', 'Female')),
            'Address': fake.address(),
            'Phone': fake.phone_number(),
        }

    def get_sensor_data(self, data_address):
        # Get sensor data for a specific data address
        address_components = data_address.split('.')
        current_data = self.sensor_data
        for component in address_components:
            current_data = current_data.get(component, {})
        return current_data

    def generate_json_string(self, data_address):
        # Generate a JSON string for the requested sensor data
        sensor_data = self.get_sensor_data(data_address)
        if 'Temperature' in data_address:
            return json.dumps(sensor_data, indent=2)
        return json.dumps(sensor_data, indent=2)

    def print_patient_data(self):
        # Print patient data
        print("Patient Data:")
        print(json.dumps(self.sensor_data['PatientInfo'], indent=2))

    def print_sensor_data(self, user_input):
        # Print sensor data based on user input
        print("Sensor Data:")
        if user_input.lower() == 'all':
            print(json.dumps(self.sensor_data, indent=2))
        else:
            try:
                print(self.generate_json_string(user_input))
            except KeyError:
                print(f"Sensor data for {user_input} not found.")

    def mmHg_to_kPa(self, mmHg_value):
        # Placeholder conversion from mmHg to kPa
        return mmHg_value * 0.133322

    def percentage_to_fractional(self, percentage_value):
        # Placeholder conversion from percentage to fractional
        return percentage_value / 100.0

# Example usage:
sensor_system = MedicalSensorSystem()

# Display and return patient data
sensor_system.print_patient_data()

# Get and print data based on user input
user_input = input("Enter the sensor data you want (e.g., 'all', 'HeartRate', 'Temperature.Celsius' or 'Temperature.Fahrenheit'): ")
sensor_system.print_sensor_data(user_input)


