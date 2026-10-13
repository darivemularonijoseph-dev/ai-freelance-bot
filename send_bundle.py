import requests
import json

token = '8725679037:AAFDFl8xDz9WeZiA_Jdozb9rAZQ37WSRKI4'
chat_id = 8856823322
url = f'https://api.telegram.org/bot{token}/sendDocument'

with open('phone_bundle.zip', 'rb') as f:
    files = {'document': f}
    data = {'chat_id': chat_id, 'caption': 'Here is your complete 24/7 Phone Server Bundle (phone_bundle.zip)!'}
    r = requests.post(url, data=data, files=files).json()
    print("phone_bundle.zip sent:", r.get('ok'))

with open('setup_phone.sh', 'rb') as f:
    files = {'document': f}
    data = {'chat_id': chat_id, 'caption': '1-Click installer script for Termux on Android (setup_phone.sh)'}
    r = requests.post(url, data=data, files=files).json()
    print("setup_phone.sh sent:", r.get('ok'))
