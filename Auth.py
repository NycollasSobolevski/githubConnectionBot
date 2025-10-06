import json
import secrets
import requests
import sys
import time
import jwt

import _secrets as s
import Conversions

def login():
    data = request_device_code()
    print(f"Visit: {data.verification_uri}")
    print(f"Enter code: {data.user_code}")

    poll_for_token(data)

    print("Successfully authenticated")

def org_login():
    save_installations()
    gen_installation_access_token()

def request_device_code() -> Conversions.RequestDeviceResponse :
    uri = "https://github.com/login/device/code"
    parameters = {"client_id": s.CLIENT_ID}
    headers = {"Accept": "application/json"}

    res = requests.post(uri, params=parameters, headers=headers)

    if(res.status_code != 200):
        print(f"error on make request: {res.text}")
        return

    data = Conversions.RequestDeviceResponse(res.json())

    return data

def request_token(device_info: Conversions.RequestDeviceResponse):
    uri = "https://github.com/login/oauth/access_token"
    parameters = {
        "client_id": s.CLIENT_ID,
        "device_code": device_info.device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    }
    headers = {"Accept": "application/json"}
    res = requests.post(uri, params=parameters, headers=headers)

    if (res.status_code != 200):
        print(f"Error on request token: {res.text}")
        return

    data = Conversions.RequestTokenReponse(res.json())
    return data

def poll_for_token(deviceInfo: Conversions.RequestDeviceResponse):
    trying = True
    while trying:
        response = request_token(deviceInfo)

        if not response.successfull:
            match response.error:
                case "authorization_pending":
                    time.sleep(deviceInfo.interval)
                    continue

                case "slow_down":
                    time.sleep(deviceInfo.interval + 5)
                    continue

                case "expired_token":
                    print("The device code has expired. Please run `login` again")
                    sys.exit(1)

                case "access_denied":
                    print("Login canceled by user!")
                    sys.exit(1)
        else:
            trying = False

    with open(".token", "w") as file:
        file.write(response.access_token)
    return

#! ==================== NEW LOGIN ==========================

def get_jwt_token() -> str:
    app_id = s.CLIENT_ID
    key_path = './_keys/github_private_key.pem'
    key = ''

    with open(key_path, 'r') as f:
        key = f.read()

    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + (10 * 60),
        'iss': app_id
    }

    jwt_token = jwt.encode(payload, key, algorithm='RS256')
    return jwt_token

def gen_installation_access_token(installation_id=None, headers = {'Authorization': f'bearer {get_jwt_token()}'}):
    installations = []
    with open('installationToken.json', 'r') as file:
        installations = json.loads(file.read())
    
    if installation_id == None:
        installation_id = installations[0]['installation_id']

    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    print(url)
    response = requests.post(url, headers=headers)

    if response.status_code != 201:
        raise Exception(f"Erro ao solicitar access token\n\n {response.text}")

    token = response.json()['token']
    finded = False
    for data in installations:
        if installation_id == data['installation_id']:
            data['token'] = token
            finded = True

    if not finded:
        installations.append({
            'client_id': f'',
            'installation_id': f'{installation_id}',
            'token': f'{token}'
        })
    
    with open('installationToken.json', 'w') as file:
        file.write(json.dumps(installations))

def save_installations():
    headers = {
        'Authorization': f'bearer {get_jwt_token()}',
        'Accept': 'application/vnd.github+json'
    }

    response = requests.get('https://api.github.com/app/installations', headers=headers)
    installations = response.json()
    data = []

    for instalation in installations:
        data.append({
            "installation_id": f"{instalation['id']}",
            "client_id": f"{instalation['client_id']}",
            "token": ""
        })

    with open("installationToken.json", "w") as file:
        file.writelines(json.dumps(data))

