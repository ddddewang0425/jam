import json
with open("config.json","r") as f:
    config = json.load(f)
def get_firebase():
    return config["firebase"]
def get_gptapi():
    return config["gptapi"]
def get_myuuid():
    return config["myuuid"]
