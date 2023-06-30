import paho.mqtt.client as mqtt
import mysql.connector
import json

# MQTT broker details
mqtt_broker = "91.121.93.94"
mqtt_port = 1883

# Database connection details
db_host = "127.0.0.1"
db_port = 3306
db_user = "root"
db_password = ""
db_name = "energy_meter"

# Function to update the MySQL database with received data
def update_db(topic, payload):
    # Create a connection to the MySQL database
    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # SQL query to insert data into the database table
    query = f"INSERT INTO data (topic, message) VALUES (%s, %s)"

    # Data to be inserted
    data = (topic, payload)

    # Execute the query
    cursor.execute(query, data)
    conn.commit()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

# Callback function when the client connects to the MQTT broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code: {rc}")
    # Subscribe to topics upon successful connection
    client.subscribe("device/Voltage")
    client.subscribe("device/Current")
    client.subscribe("device/Power")
    client.subscribe("device/kWh")

# Callback function when a message is received on a subscribed topic
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()}")     
    # print(msg.topic)
    
    # get the payload and the topic
    topic = msg.topic
    payload = msg.payload.decode()
    
    # Convert the payload to a float value
    try:
        payload_value = float(payload)
    except ValueError:
        print(f"Invalid payload: {payload}")
        return
    
    # update the database
    update_db(topic, payload_value)

# Create an MQTT client instance
client = mqtt.Client()

# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port)

# Loop continuously to process MQTT network traffic, but avoid blocking the main thread
client.loop_forever()
