import requests
import random
import time

URL = "http://127.0.0.1:8000/temperature"

drones = [1, 2, 3]

while True:

    for drone_id in drones:

        temperature = random.randint(0, 12)

        print("Drone:", drone_id)
        print("Temperature:", temperature, "°C")

        response = requests.post(
            URL,
            params={
                "drone_id": drone_id,
                "temperature": temperature
            }
        )

        print("Backend response:")
        print(response.json())
        print("----------------------")

    time.sleep(5)