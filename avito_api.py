from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from hashlib import sha256

def create_driver(
    headless = True, 
    clear_cookies = False
):
    options = Options()
    if headless:
        options.headless = True
        options.add_argument("--headless")
    if clear_cookies:
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows; U; Windows NT 10.4;; en-US) AppleWebKit/603.21 (KHTML, like Gecko) Chrome/49.0.3713.352 Safari/603.2 Edge/10.30739")
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", False)
        options.set_preference("browser.cache.offline.enable", False)
        options.set_preference("network.http.use-cache", False) 
    driver = Firefox(options=options)
    if clear_cookies:
        driver.delete_all_cookies()
    driver.get('about:blank')
    return driver

def close_driver(driver: Firefox):
    driver.close()
    driver.quit()

def avito_search(
    driver: Firefox, 
    query: str,
    page: int, 
    url = "https://www.avito.ru/all/noutbuki?cd=1&p={1}&q={0}", 
    cookie = {}
):
    driver.get(url.format(query, page))
    for a in [{"name": i[0], "value": i[1]} for i in cookie.items()]:
        driver.add_cookie(a)
    driver.get(url.format(query, page))

    objects = []
    for element in driver.find_elements(By.CSS_SELECTOR, "div[data-marker=\"item\"]"):
        try:
            url = element.find_element(By.CSS_SELECTOR, "a[itemprop=\"url\"]").get_attribute("href")
            name = element.find_element(By.CSS_SELECTOR, "h3[itemprop=\"name\"]").text
            price, small_description, *_ = map(lambda a: a.text, element.find_elements(By.TAG_NAME, "p"))
            price = int("".join(list(filter(lambda a: a in "0123456789", price))))
            path = url.removeprefix("https://www.avito.ru/").split("?")[0]

            objects.append({
                "url": url,
                "path": path,
                "name": name,
                "price": price,
                "small_description": small_description,
                "hash": sha256(path.encode('utf-8')).hexdigest()
            })
        except:
            pass
    
    return objects

def avito_get_info(
    driver: Firefox, 
    path: str, 
    url = "https://www.avito.ru/{0}", 
    times = 0
):
    if times == 10: return {}

    params = {}
    description = "N/A"

    try:
        driver.get(url.format(path))

        params_div = driver.find_element(By.CSS_SELECTOR, "div[data-marker=\"item-view/item-params\"]")

        for param in params_div.find_elements(By.TAG_NAME, "p"):
            param_text = param.text
            if ": " in param_text:
                k, v = param_text.split(": ")
                params[k] = v

        description = driver.find_element(By.CSS_SELECTOR, "div[itemprop=\"description\"]").text
    except NoSuchElementException: pass
    except Exception:
        return avito_get_info(driver, path, url, times=times+1)

    return {"params": params, "description": description}

def get_benchmark_score(
    driver: Firefox, 
    cpu: str, 
    gpu: str, 
    cpu_url = "https://browser.geekbench.com/search?q={0}", 
    gpu_url = "https://browser.geekbench.com/search?k=v6_compute&q={0}"
):
    cpu_score = None
    gpu_score = None

    if cpu != None:
        driver.get(cpu_url.format(cpu.split(",")[0]))

        cpu_score = 0
        score_size = 0
        for column in driver.find_elements(By.CLASS_NAME, "list-col-inner"):
            for score in column.find_elements(By.CLASS_NAME, "list-col-text-score"):
                cpu_score += int(score.text)
                score_size += 1
        if cpu_score != 0 and score_size != 0:
            cpu_score = int(cpu_score / score_size)
        else:
            cpu_score = None

    if gpu != None:
        driver.get(gpu_url.format(gpu))

        gpu_score = 0
        score_size = 0
        for column in driver.find_elements(By.CLASS_NAME, "list-col-inner"):
            for score in column.find_elements(By.CLASS_NAME, "list-col-text-score"):
                gpu_score += int(score.text)
                score_size += 1
        if gpu_score != 0 and score_size != 0:
            gpu_score = int(gpu_score / score_size)
        else:
            gpu_score = None
    
    if gpu_score == None:
        gpu_score = cpu_score

    return {"cpu": cpu_score, "gpu": gpu_score}

def pack_thinkpad(
    driver: Firefox,
    item: dict[str, object], 
    info: dict[str, str],
    minimal = True
):
    g = lambda x,y,m=lambda a:a: m(x[y]) if y in x else None

    def disk_size(s):
        t = ""
        for c in s:
            if c in "0123456789":
                t += c
            else:
                break
        return int(t)
    
    def disk_type(s):
        t = ""
        for c in s:
            if c in "SDH":
                t += c
            else:
                break
        return t

    data = {
        "url": item["url"],
        "hash": item["hash"],
        "price": item["price"],
        "name": item["name"],
        "description": info["description"],
        "params": info["params"],
        "state": g(info["params"],"Состояние"),
        "manufacturer": g(info["params"],"Производитель"),
        "screen_diagonal": g(info["params"],"Диагональ, дюйм"),
        "screen_size": g(info["params"],"Разрешение экрана"),
        "cpu": g(info["params"],"Процессор"),
        "cpu_cores": g(info["params"],"Количество ядер процессора",int),
        "ram": g(info["params"],"Оперативная память, ГБ",int),
        "disk_type": g(info["params"],"Конфигурация накопителей",disk_type),
        "disk_size": g(info["params"],"Объем накопителей, ГБ",disk_size),
        "gpu": g(info["params"],"Видеокарта"),
        "os": g(info["params"],"Операционная система"),
    }

    data["benchmarks"] = get_benchmark_score(driver, data["cpu"], data["gpu"])

    if minimal:
        del data["description"]
        del data["name"]
        del data["params"]
        del data["os"]
        del data["cpu_cores"]
        del data["screen_diagonal"]
        del data["state"]
        del data["manufacturer"]

    return data