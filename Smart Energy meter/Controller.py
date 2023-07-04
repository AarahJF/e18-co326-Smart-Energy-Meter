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

# Function to retrieve the latest data from the database
def retrieve_latest():
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

    # SQL query to retrieve data
    query = "SELECT * FROM data ORDER BY updatedAt DESC LIMIT 40"  # Replace 'data' with your table name

    # Execute the query
    cursor.execute(query)

    # Fetch all the rows from the result set
    rows = cursor.fetchall()
    print(rows[0])
    # Process the retrieved data for each sensor separately
    sensor1_data = []
    sensor2_data = []
    sensor3_data = []
    sensor4_data = []
    # Add more arrays for other sensors if needed

    for row in rows:
        # each row will be a tuple so we need to access each property and create a json object
        data = {
            "topic": row[0],
            "value": row[1],
            "updatedAt": str(row[2])
        }

        # Append data to the corresponding sensor array based on the topic
        if row[0] == "device/Voltage":
            sensor1_data.append(data)
        elif row[0] == "device/Current":
            sensor2_data.append(data)
        elif row[0] == "device/Power":
            sensor3_data.append(data)
        elif row[0] == "device/kWh":
            sensor4_data.append(data)
        # Add more conditions for other sensors if needed

    # Convert sensor data to JSON format
    sensor1_json_data = json.dumps(sensor1_data)
    sensor2_json_data = json.dumps(sensor2_data)
    sensor3_json_data = json.dumps(sensor3_data)
    sensor4_json_data = json.dumps(sensor4_data)
    # Add more JSON strings for other sensors if needed

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Return the JSON data for each sensor
    return sensor1_json_data, sensor2_json_data, sensor3_json_data, sensor4_json_data
    # Return more JSON data for other sensors if needed


# Publish the latest data to the specified topic
def publish_latest():
    # Get the JSON data for each sensor
    sensor1_data, sensor2_data, sensor3_data, sensor4_data= retrieve_latest()
    # Get more JSON data for other sensors if needed

    # Print the retrieved data on the console
    print("Sensor 1 Data:")
    print(sensor1_data)
    print("Sensor 2 Data:")
    print(sensor2_data)
    print("Sensor 3 Data:")
    print(sensor3_data)
    print("Sensor 4 Data:")
    print(sensor4_data)
    # Print more data for other sensors if needed

    # Create an MQTT client instance
    client = mqtt.Client()

    # Connect to the MQTT broker
    client.connect(mqtt_broker, mqtt_port)

    # Publish data for Sensor 1 to topic "Sensor1_data"
    client.publish("Sensor1_data", sensor1_data)

    # Publish data for Sensor 2 to topic "Sensor2_data"
    client.publish("Sensor2_data", sensor2_data)
    # Publish more data for other sensors if needed
    # Publish data for Sensor 1 to topic "Sensor1_data"
    client.publish("Sensor3_data", sensor3_data)

    # Publish data for Sensor 2 to topic "Sensor2_data"
    client.publish("Sensor4_data", sensor4_data)
    # Publish more data for other sensors if needed

    # Disconnect from the MQTT broker
    client.disconnect()

   


# Start executing the function
publish_latest()
