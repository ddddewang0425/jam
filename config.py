import json
with open("config.json","r") as f:
    config = json.load(f)
def get_firebase(read=False):
    if read:
        with open(config["firebase"], "r") as f:
            return json.load(f)
    return config["firebase"]
def get_gptapi(read=True):
    if read:
        with open(config["gptapi"], "r") as f:
            return f.read().strip()
    return config["gptapi"]
def get_myuuid(read=True):
    if read:
        with open(config["myuuid"], "r") as f:
            return f.read().strip()
    return config["myuuid"]