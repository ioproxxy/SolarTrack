import json


with open("marine-fusion-459216-n9-5094ec24fc92.json") as f:
    content = json.load(f)
    print(json.dumps(content))
