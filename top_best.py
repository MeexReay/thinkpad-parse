import json
import webbrowser

items = [json.loads(i) for i in open("thinkpads.txt", "r").readlines()]

avg_ram = 0
avg_gpu = 0
avg_cpu = 0
avg_disk = 0
min_price = -1
max_price = -1

for item in items:
    if item["ram"] != None: avg_ram = (avg_ram + item["ram"]) / 2.0 if avg_ram != 0 else item["ram"]
    if item["benchmarks"]["cpu"] != None: avg_cpu = (avg_cpu + item["benchmarks"]["cpu"]) / 2.0 if avg_cpu != 0 else item["benchmarks"]["cpu"]
    if item["benchmarks"]["gpu"] != None: avg_gpu = (avg_gpu + item["benchmarks"]["gpu"]) / 2.0 if avg_gpu != 0 else item["benchmarks"]["gpu"]
    if item["disk_size"] != None: avg_disk = (avg_disk + item["disk_size"]) / 2.0 if avg_disk != 0 else item["disk_size"]
    if min_price == -1 or min_price > item["price"]: min_price = item["price"]
    if max_price == -1 or max_price < item["price"]: max_price = item["price"]

def get_score(item):
    quality = int(((item["ram"] / avg_ram) + \
        (item["benchmarks"]["cpu"] / avg_cpu) + \
        (item["benchmarks"]["gpu"] / avg_gpu) + \
        (item["disk_size"] / avg_disk)) / 4 * 1000)
    
    return ((max_price - (item["price"] - min_price)) / min_price) * 1500 + quality

def key_filter(item):
    if item["ram"] == None: return False
    if item["benchmarks"]["cpu"] == None: return False
    if item["benchmarks"]["gpu"] == None: return False
    if item["disk_size"] == None: return False
    return True

result = list(filter(key_filter, items))
result = sorted(result, key = get_score, reverse=True)

for item in result:
    webbrowser.open_new_tab(item["url"])
    print(f"{item} (score: {get_score(item)})")
    input()