import os
import json

from test.test_reprlib import r

import Auth
import Excel
import Github

data_path = "./data.json"
token_path = "./.token"
sheet_path = "./test.xlsx"
token = ""
settings = {}

if not os.path.exists(token_path):
    Auth.login()

with open(token_path, 'r') as file:
    token = file.read()

with open(data_path, 'r') as file:
    obj = json.load(file)
    settings = obj

if not os.path.exists(sheet_path):
    print("aaaaaaa")
    Excel.verify_if_exists(settings, sheet_path)

for proj in settings['projects']:
    issues = Github.get_project_items(proj['number'], token)
    Excel.update_excel("./test.xlsx", proj['name'], issues)

