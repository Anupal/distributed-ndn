import json
import random
import faker


class MedicalSensorSystem:
    def __init__(self):
        self.sensor_data = {
            "patientinfo": self.generate_fake_patient_data(),
            "heartrate": {
                "ecg": random.randint(60, 100),
                "ppg": random.randint(60, 100),
            },
            "bloodpressure": {
                "invasive": {
                    "mmHg": random.randint(90, 140),
                    "kPa": self.mmHg_to_kPa(random.randint(90, 140)),
                },
                "noninvasive": {
                    "mmHg": random.randint(90, 140),
                    "kPa": self.mmHg_to_kPa(random.randint(90, 140)),
                },
            },
            "glucose": random.uniform(70, 150),
            "temperature": {
                "celsius": random.uniform(36.0, 38.0),
                "fahrenheit": random.uniform(96.8, 100.4),
            },
            "oxygensaturation": {
                "percentage": random.uniform(95, 100),
                "fractional": self.percentage_to_fractional(random.uniform(95, 100)),
            },
            "respiratoryRate": random.randint(12, 20),
            "movement": {
                "accelerometer": {
                    "x": random.uniform(-1, 1),
                    "y": random.uniform(-1, 1),
                    "z": random.uniform(-1, 1),
                },
                "gyroscope": {
                    "roll": random.uniform(-180, 180),
                    "pitch": random.uniform(-90, 90),
                    "yaw": random.uniform(-180, 180),
                },
            },
            "eeg": random.uniform(0, 100),
        }

    def generate_fake_patient_data(self):
        # Generate fake patient data using the Faker library
        fake = faker.Faker()
        return {
            "PatientID": fake.uuid4(),
            "FirstName": fake.first_name(),
            "LastName": fake.last_name(),
            "Age": fake.random_int(min=18, max=99),
            "Gender": fake.random_element(elements=("Male", "Female")),
        }

    def get_sensor_data(self, data_address):
        # Get sensor data for a specific data address
        address_components = data_address.split("/")
        current_data = self.sensor_data
        for component in address_components:
            current_data = current_data.get(component, {})
        return current_data

    def generate_json_string(self, data_address):
        try:
            sensor_data = self.get_sensor_data(data_address)
        except KeyError:
            return json.dumps({"message": "Data not found!"})
        return json.dumps(sensor_data)

    def mmHg_to_kPa(self, mmHg_value):
        # Placeholder conversion from mmHg to kPa
        return mmHg_value * 0.133322

    def percentage_to_fractional(self, percentage_value):
        # Placeholder conversion from percentage to fractional
        return percentage_value / 100.0
