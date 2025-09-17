import requests

import Auth

# url = 'https://api.github.com/events'

# org = ''
# project_number = 2
# proj = f'/orgs/{org}/projectsV2/{project_number}/items'

# response = requests.get(url)

# if response.status_code == 200:
#     print('foi meu querido')
#     print(response.json())
# else:
#     print(f"failed with status: {response.status_code}")


# Auth.request_device_code()
Auth.login()