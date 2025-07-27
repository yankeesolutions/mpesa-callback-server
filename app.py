from flask import Flask, request, jsonify
import requests
import base64
import datetime
import json

app = Flask(__name__)

# M-PESA CREDENTIALS
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET'
shortcode = 'YOUR_SHORTCODE'
passkey = 'YOUR_PASSKEY'
business_shortcode = shortcode
callback_url = 'https://yankeemailer-qjpj.onrender.com/stk_callback'

# GET ACCESS TOKEN
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return json.loads(response.text)['access_token']

# GENERATE PASSWORD
def generate_password():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data = business_shortcode + passkey + timestamp
    encoded = base64.b64encode(data.encode()).decode()
    return encoded, timestamp

# STK PUSH ENDPOINT
@app.route('/stkpush', methods=['POST'])
def stk_push():
    data = request.get_json()
    phone = data['phone']
    amount = data['amount']

    access_token = get_access_token()
    password, timestamp = generate_password()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": business_shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": "Test",
        "TransactionDesc": "Test STK Push"
    }

    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", 
                             json=payload, headers=headers)

    return jsonify(response.json())

# CALLBACK ENDPOINT
@app.route('/')
def home():
    return "M-PESA Callback Server is running."
@app.route('/stk_callback', methods=['POST'])
def stk_callback():
    data = request.get_json()
    print("📥 Received STK Callback:\n", json.dumps(data, indent=4))

    try:
        callback = data['Body']['stkCallback']
        result_code = callback.get('ResultCode', None)
        result_desc = callback.get('ResultDesc', '')

        if result_code == 0:
            # Payment was successful
            metadata = callback['CallbackMetadata']['Item']
            parsed = {item['Name']: item.get('Value', '') for item in metadata}

            amount = parsed.get('Amount')
            phone = parsed.get('PhoneNumber')
            receipt = parsed.get('MpesaReceiptNumber')
            date = parsed.get('TransactionDate')

            print("✅ PAYMENT SUCCESS")
            print(f"Amount: {amount}")
            print(f"Phone: {phone}")
            print(f"Receipt: {receipt}")
            print(f"Date: {date}")
        else:
            # Payment failed or cancelled
            print("❌ PAYMENT FAILED or CANCELED")
            print(f"Reason: {result_desc}")

    except Exception as e:
        print("⚠️ Error processing callback:", e)

    return jsonify({"ResultCode": 0, "ResultDesc": "Callback received successfully"})

