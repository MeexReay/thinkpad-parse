from avito_api import *
import threading
import json
import time

URL = "https://www.avito.ru/all/noutbuki?cd=1&f=ASgCAgECA0XGmgwUeyJmcm9tIjo0MDAwLCJ0byI6MH2coRQUeyJmcm9tIjo0LCJ0byI6bnVsbH2eoRQWeyJmcm9tIjoyMDAsInRvIjpudWxsfQ&q={0}&s=1&p={1}"
COOKIE = json.load(open("cookies.json", "r"))
THREADS = 10
PAGES_PER_THREAD = 10
HEADLESS = True

def on_pack(pack):
    for i in open("thinkpads.txt", mode="r").readlines():
        if json.loads(i)["hash"] == pack["hash"]:
            return
    open("thinkpads.txt", mode="a").write(json.dumps(pack,ensure_ascii=False).replace("\n","\\n")+"\n")

def parse_page(page):
    driver = create_driver(headless = HEADLESS)

    for p in range(1, PAGES_PER_THREAD + 1):
        p = page * PAGES_PER_THREAD + p

        print(p)

        for item in avito_search(driver, "thinkpad", p, url=URL, cookie=COOKIE):
            info = avito_get_info(driver, item["path"])
            pack = pack_thinkpad(driver, item, info)

            print(pack)

            on_pack(pack)

    close_driver(driver)

threads = []

for page in range(THREADS):
    thread = threading.Thread(target=parse_page, args=(page,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()