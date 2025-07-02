from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

# Load MongoDB URI from .env file
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["webhookdb"]
collection = db["webhook_events"]

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📥 Webhook received:", data)

    try:
        event_type = request.headers.get('X-GitHub-Event')

        if event_type == "push":
            payload = {
                "author": data["pusher"]["name"],
                "to_branch": data["ref"].split("/")[-1],
                "action": "push",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        elif event_type == "pull_request":
            payload = {
                "author": data["pull_request"]["user"]["login"],
                "from_branch": data["pull_request"]["head"]["ref"],
                "to_branch": data["pull_request"]["base"]["ref"],
                "action": "pull_request",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        elif event_type == "merge":
            payload = {
                "author": data["sender"]["login"],
                "from_branch": data["pull_request"]["head"]["ref"],
                "to_branch": data["pull_request"]["base"]["ref"],
                "action": "merge",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        else:
            return jsonify({"message": "Event type not handled"}), 200

        collection.insert_one(payload)
        return jsonify({"message": "Stored successfully"}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/events')
def get_events():
    try:
        events = list(collection.find().sort("timestamp", -1))
        formatted = []

        for event in events:
            action = event.get("action")
            author = event.get("author")
            from_branch = event.get("from_branch", "")
            to_branch = event.get("to_branch", "")
            timestamp = event.get("timestamp")

            formatted_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d %b %Y - %I:%M %p UTC")

            if action == "push":
                formatted.append(f'{author} pushed to {to_branch} on {formatted_time}')
            elif action == "pull_request":
                formatted.append(f'{author} submitted a pull request from {from_branch} to {to_branch} on {formatted_time}')
            elif action == "merge":
                formatted.append(f'{author} merged branch {from_branch} to {to_branch} on {formatted_time}')

        return jsonify(formatted)

    except Exception as e:
        print("❌ Failed to load events:", e)
        return jsonify([]), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


