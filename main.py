import os
import json
import sys 

import Auth
import Excel
import Github
import Exceptions
import Environment as e

data_path = "./data.json"
token_path = e.get_env("INSTALLATION_TOKEN_PATH")
sheet_path = e.get_env("OUTPUT_FILE_PATH")
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


for proj in settings['projects']:

    if not os.path.exists(proj['sheetPath']):
        Excel.verify_if_exists(proj)
    
    issues = []
    try:
        issues = Github.get_project_items(proj, token)
    except Exceptions.UnauthorizedError:
        Auth.org_login()
        with open(token_path, 'r') as file:
            token = file.read()
        issues = Github.get_project_items(proj, token)

    finally:
        Excel.update_excel_by_df(sheet_path, proj['name'], issues)

