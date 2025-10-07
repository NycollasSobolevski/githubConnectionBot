import os
from dotenv import load_dotenv

load_dotenv()

def get_env(variable):
    var = os.getenv(variable)
    return var if var != None else ""