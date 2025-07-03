from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI not found in .env file")

print("Loaded MONGO_URI:", MONGO_URI)

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["webhook_db"]
collection = db["events"]

# Flask app setup
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    # Fetch recent 10 events
    events = collection.find().sort("timestamp", -1).limit(10)
    return render_template("index.html", events=events)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data:
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        collection.insert_one({
            "event_type": event_type,
            "payload": data,
            "timestamp": datetime.utcnow()
        })
        return jsonify({"message": f"{event_type} event received"}), 200
    return jsonify({"error": "No data received"}), 400

@app.route('/events', methods=['GET'])
def get_events():
    events = collection.find().sort("timestamp", -1).limit(10)
    formatted = [
        f"{event.get('event_type', 'unknown')} - {event.get('timestamp')}"
        for event in events
    ]
    return jsonify(formatted)

if __name__ == '__main__':
    app.run(debug=True)






