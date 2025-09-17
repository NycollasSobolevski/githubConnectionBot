import requests
import sys
import time

import _secrets as s

class RequestDeviceResponse:
    def __init__(self, json):
        self.device_code = json["device_code"]
        self.user_code = json["user_code"]
        self.verification_uri = json["verification_uri"]
        self.interval = json["interval"]
        self.expires_in = json["expires_in"]

class RequestTokenReponse:
    def __init__(self, json):
        self.successfull = True
        try:
            print(json["access_token"])
        except:
            self.successfull = False
        
        if(not self.successfull):
            self.error = json["error"]
            self.error_description = json["error_description"]
            self.error_uri = json["error_uri"]
        else:
            self.access_token = json["access_token"]
            self.scope = json["scope"]
            self.token_type = json["token_type"]

def login():
    data = request_device_code()
    print(f"Visit: {data.verification_uri}")
    print(f"Enter code: {data.user_code}")

    poll_for_token(data)

    print("Successfully authenticated")

def request_device_code() -> RequestDeviceResponse :
    uri = "https://github.com/login/device/code"
    parameters = {"client_id": s.CLIENT_ID}
    headers = {"Accept": "application/json"}

    res = requests.post(uri, params=parameters, headers=headers)

    if(res.status_code != 200):
        print(f"error on make request: {res.text}")
        return

    data = RequestDeviceResponse(res.json())

    return data

def request_token(device_info: RequestDeviceResponse):
    uri = "https://github.com/login/oauth/access_token"
    parameters = {
        "client_id": s.CLIENT_ID,
        "device_code": device_info.device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    }
    headers = {"Accept": "application/json"}
    res = requests.post(uri, params=parameters, headers=headers)

    print(res.text)

    if (res.status_code != 200):
        print(f"Error on request token: {res.text}")
        return

    data = RequestTokenReponse(res.json())
    return data

def poll_for_token(deviceInfo: RequestDeviceResponse):
    debug_index = 0
    trying = True
    while trying:
        debug_index += 1
        print(f"{debug_index}" )
        response = request_token(deviceInfo)

        if not response.successfull:
            match response.error:
                case "authorization_pending":
                    print("authorization_pending")
                    time.sleep(deviceInfo.interval)
                    continue

                case "slow_down":
                    print("slow_down")
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
