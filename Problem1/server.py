from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Function to register the company and get credentials

def register_company(roll_no, access_code):
    registration_url = "http://20.244.56.144/train/register"
    registration_data = {
        "companyName": "Train Central",
        "ownerName": "Nilabja Sanyal",
        "rollNo": '2005736',
        "ownerEmail": "nilabja.sanyal@gmail.com",
        "accessCode": 'oJnNPG'
    }
    response = requests.post(registration_url, json=registration_data)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Company registration failed")

# Function to get the authorization token
def get_authorization_token(client_id, client_secret):
    auth_url = "http://20.244.56.144/train/auth"
    auth_data = {
        "companyName": "Train Central",
        "clientID": client_id,
        "clientSecret": client_secret
    }
    response = requests.post(auth_url, json=auth_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Authorization token retrieval failed")

# Function to get train details from John Doe Railways
def get_train_details(token):
    trains_url = "http://20.244.56.144/train/trains"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(trains_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch train details")

# Function to filter trains and sort them based on specified criteria
def filter_and_sort_trains(trains):
    now = datetime.now()
    twelve_hours_later = now + timedelta(hours=12)

    filtered_trains = []
    for train in trains:
        departure_time = datetime(
            now.year, now.month, now.day,
            train["departureTime"]["Hours"],
            train["departureTime"]["Minutes"],
            train["departureTime"]["Seconds"]
        )

        # Ignore trains departing in the next 30 minutes
        if now + timedelta(minutes=30) < departure_time < twelve_hours_later:
            filtered_trains.append(train)

    # Sort trains based on specified criteria
    sorted_trains = sorted(
        filtered_trains,
        key=lambda t: (t["price"]["AC"], t["price"]["sleeper"], t["delayedBy"]),
        reverse=True
    )
    return sorted_trains

@app.route("/trains", methods=["GET"])
def get_trains_schedule():
    try:
        # Register the company and get credentials
        registration_response = register_company('2005736', 'oJnNPG')
        client_id = registration_response["clientID"]
        client_secret = registration_response["clientSecret"]


        token = get_authorization_token(client_id, client_secret)

        
        trains = get_train_details(token)


        sorted_trains = filter_and_sort_trains(trains)

        return jsonify(sorted_trains)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
