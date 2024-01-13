from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = 'cn2015'  # Replace with your verify token

@app.route('/newmessage', methods=['GET', 'POST'])
def new_message():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print("WEBHOOK_VERIFIED")
                return challenge, 200
            else:
                return 'Verification token mismatch', 403
        else:
            return 'GET Method allowed only for verification'
            
    data = request.json  # Assuming the data is sent in JSON format
    print(data)  # Print the data received
    return "Received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, ssl_context=("certificate.crt", "private.key"))
