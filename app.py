from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Webhook received:", data)
    return jsonify({"message": "Webhook received successfully"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)

