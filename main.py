import os
import json
import sys 

import Auth
import Excel
import Github
import Exceptions

data_path = "./data.json"
token_path = "./installationToken.json"
sheet_path = "./test.xlsx"
token = ""
settings = {}

if '--gen-jwt' in sys.argv:
    print(Auth.get_jwt_token())
    sys.exit()
if '--save-installations' in sys.argv:
    print(Auth.save_installations())
    sys.exit()
if '--get-token' in sys.argv:
    print(Auth.gen_installation_access_token())
    sys.exit()

if not os.path.exists(token_path):
    Auth.org_login()

with open(token_path, 'r') as file:
    data = json.loads(file.read())
    token = data[0]['token']

with open(data_path, 'r') as file:
    obj = json.load(file)
    settings = obj

if not os.path.exists(sheet_path):
    Excel.verify_if_exists(settings, sheet_path)

for proj in settings['projects']:
    issues = []
    try:
        issues = Github.get_project_items(proj['number'], token)
    except Exceptions.UnauthorizedError:
        Auth.login()
        with open(token_path, 'r') as file:
            token = file.read()
        issues = Github.get_project_items(proj['number'], token)

    finally:
        Excel.update_excel("./test.xlsx", proj['name'], issues)

