from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "M-PESA Callback Server is live."

@app.route('/mpesa_callback', methods=['POST'])
def mpesa_callback():
    data = request.json
    print("Received M-PESA callback:", data)
    return "Callback received", 200

if __name__ == '__main__':
    app.run()
