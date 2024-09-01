import json

hash = input("hash > ")

for item in open("thinkpads.txt", "r").readlines():
    item = json.loads(item)
    
    if item["hash"] == hash:
        print(json.dumps(item, indent=2))

        break