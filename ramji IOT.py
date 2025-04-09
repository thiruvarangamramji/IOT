import time
import sqlite3
import Adafruit_DHT
from twilio.rest import Client

# Constants
DHT_SENSOR = Adafruit_DHT.DHT22  # or DHT11
DHT_PIN = 4  # GPIO pin number where the sensor is connected
TEMP_THRESHOLD = 30  # Temperature threshold in Celsius
TWILIO_SID = 'your_twilio_sid'  # Your Twilio SID
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'  # Your Twilio Auth Token
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'  # Your Twilio phone number
USER_PHONE_NUMBER = 'recipient_phone_number'  # User's phone number

# Create or connect to SQLite database
conn = sqlite3.connect('temperature_humidity.db')
c = conn.cursor()

# Create table to store sensor data if not exists
c.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 temperature REAL,
                 humidity REAL
             )''')
conn.commit()

# Function to send SMS alert
def send_sms_alert(temperature):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"ALERT: Temperature exceeded threshold! Current temperature is {temperature}°C.",
        from_=TWILIO_PHONE_NUMBER,
        to=USER_PHONE_NUMBER
    )
    print(f"Alert sent: {message.sid}")

# Function to read data from the sensor
def read_sensor_data():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return temperature, humidity
    else:
        print("Failed to retrieve data from the sensor.")
        return None, None

# Function to store data in the database
def store_data(temperature, humidity):
    c.execute("INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)", (temperature, humidity))
    conn.commit()
    print(f"Data stored: Temp={temperature}°C, Humidity={humidity}%")

# Main function
def main():
    while True:
        # Read data from the sensor
        temperature, humidity = read_sensor_data()

        if temperature is not None and humidity is not None:
            # Store data in the database
            store_data(temperature, humidity)

            # Check if temperature exceeds threshold and send alert
            if temperature > TEMP_THRESHOLD:
                send_sms_alert(temperature)

        # Wait for 10 minutes before reading again
        time.sleep(600)

# Run the program
if __name__ == '__main__':
    main()
