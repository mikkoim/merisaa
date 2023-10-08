from pathlib import Path
from tqdm import tqdm
from time import sleep
import re
import pandas as pd
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint
from bs4 import BeautifulSoup

def parse_direction(deg):
    suunnat = ["pohjoinen",
               "pohjoiskoillinen",
               "koillinen",
               "itäkoillinen",
               "itä",
               "itäkaakko",
               "kaakko",
               "eteläkaakko",
               "etelä",
               "etelälounas",
               "lounas",
               "länsilounas",
               "länsi",
               "länsiluode",
               "luode",
               "pohjoisluode",
               "pohjoinen"]
    return suunnat[round(deg/22.5)]

def numero_tekstiksi(n):
    """Muuttaa kokonaisluvun välillä -9999 - 9999 tekstiksi"""
    numero_map = {1: "yksi",
                2: "kaksi",
                3: "kolme",
                4: "neljä",
                5: "viisi",
                6: "kuusi",
                7: "seitsemän",
                8: "kahdeksan",
                9: "yhdeksän"}
    if abs(n) >= 10000:
        raise Exception("Vain luvut -9999 - 9999")
    if n == 0:
        return "nolla"
    if n < 0:
        ret = "miinus "
        n = abs(n)
    else:
        ret = ""
    if n < 10:
        return ret + numero_map[n]
    if n == 10:
        return ret + "kymmenen"
    if (n > 10) and (n < 20):
        r = n%10
        return ret + numero_map[r] + "toista"
    
    tuhannet = n//1000
    sadat = (n- 1000*tuhannet)//100
    kymmenet = (n - 1000*tuhannet - 100*sadat)//10
    yhdet = n%10

    tuhat_s = sadat_s = kymmen_s = yhdet_s = ""
    
    if yhdet != 0:
        yhdet_s = numero_map[yhdet]

    if kymmenet != 0:
        if kymmenet == 1:
            kymmen_s = numero_tekstiksi(kymmenet*10 + yhdet)
            yhdet_s = ""
        else:
            kymmen_s = numero_map[kymmenet] + "kymmentä"

    if sadat != 0:
        if sadat == 1:
            sadat_s = "sata"
        else:
            sadat_s = numero_map[sadat] + "sataa"

    if tuhannet != 0:
        if tuhannet == 1:
            tuhat_s = "tuhat"
        else:
            tuhat_s = numero_map[tuhannet] + "tuhatta"
    
    return ret + tuhat_s + sadat_s + kymmen_s + yhdet_s

def load_page(driver, station_id):
    driver.get(f"https://www.ilmatieteenlaitos.fi/rannikkosaa?station={station_id}")
    wait = WebDriverWait(driver, timeout=5)
    data_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-v-e11b1aae].row")))

def load_raw_data(driver):
    """Scrapeaa rannikkoaseman viimeisimmät havainnot ja palauttaa ne sellaisessa muodossa kuin ne ovat sivulla"""

    # Lataa sivun html
    html = driver.page_source
    soup = BeautifulSoup(html, features="html5")

    # Hae havainnot
    havainnot_section = soup.select("section[aria-label^='Viimeisimmät säähavainnot']")
    havainnot = list(havainnot_section[0])[0]

    data_section = list(havainnot.children)[2]
    aikaleima_raw = list(havainnot.children)[0].get_text()
    data_raw = [x.get_text() for x in data_section.children]
    return aikaleima_raw, data_raw

def create_data_dict(data_raw):
    data_vars = ['Lämpötila',
            'Kastepiste',
            'Kosteus',
            'Tuuli',
            'Tuulen suunta',
            'Tuulen puuska',
            'Näkyvyys',
            'Pilvisyys',
            'Paine',
            'Sade']

    data_dict = {}
    for v in data_vars:
        data_dict[v] = None
        for data_row in data_raw:
            if data_row.startswith(v):
                data_dict[v] = data_row.replace(v, "").strip()
    return data_dict

def parse_aikaleima(aikaleima_raw):
    """Muuttaa verkkosivulta poimitun aikaleiman luettavaksi tekstiksi
    esim 'Viimeisin säähavainto: La 7.10. 14:40  ' -> 'neljätoista neljäkymmentä'
    """
    aika = aikaleima_raw.split(" ")[4]
    tunti, minuutti = aika.split(":")
    return numero_tekstiksi(int(tunti)) + " " + numero_tekstiksi(int(minuutti))

def parse_data_dict(data_dict):
    lampotila = round(float(data_dict["Lämpötila"].split(" ")[0].replace(",", ".")))
    lampotila_str = numero_tekstiksi(lampotila)

    tuuli = int(data_dict["Tuuli"].split(" ")[0])
    tuuli_str = numero_tekstiksi(tuuli)

    tuulen_suunta = int(re.search(r"\((\d+)\°\)", data_dict["Tuulen suunta"]).group(1))
    tuulen_suunta_str = parse_direction(tuulen_suunta)

    if data_dict["Sade"] is None:
        sade_str = ""
    else:
        sade_str = "sadetta"

    if data_dict["Pilvisyys"] is None:
        pilvisyys_str = ""
    else:
        pilvisyys_str = " ".join(data_dict["Pilvisyys"].split(" ")[:-1]).lower()

    if data_dict["Näkyvyys"] is None:
        nakyvyys_str = ""
    else:
        nakyvyys = data_dict["Näkyvyys"].split(" ")[0]
        if nakyvyys == "yli":
            nakyvyys_str = "hyvä näkyvyys"
        else:
            nakyvyys = round(float(nakyvyys.replace(",", ".")))
            nakyvyys_str = numero_tekstiksi(nakyvyys)
        

    asema_str = f"{lampotila_str} {tuulen_suunta_str} {tuuli_str} {sade_str} {pilvisyys_str} {nakyvyys_str}"
    return asema_str

def rannikkoasema_pipeline(driver, asema):
    try:
        load_page(driver, short2value[asema])
        aikaleima_raw, data_raw = load_raw_data(driver)
        if len(data_raw) == 0:
            sleep(2)
            aikaleima_raw, data_raw = load_raw_data(driver)
        data_dict = create_data_dict(data_raw)
        aikaleima_str = parse_aikaleima(aikaleima_raw)
        asema_str = parse_data_dict(data_dict)
    except Exception:
        return "", "ei havaintoja"
    return aikaleima_str, asema_str

def saatiedotus_cleaner(s):
    saatiedotus_header = s.split("\n")[0]
    aika = numero_tekstiksi(int(saatiedotus_header.split(" ")[-1]))
    s = s.replace(saatiedotus_header, f"Säätiedotus merenkulkijoille tänään kello {aika}")

    s = s.replace("Säätiedotus 2 vrk", "kahden vuorokauden säätiedotus")


    # Korjaa pilkulliset numerot. 2,5 -> "kaksi pilkku viisi"
    pilkku_numerot = re.findall(r"\b\d+,\d+\b", s)
    for p in pilkku_numerot:
        s = s.replace(p, p.replace(",", " pilkku "))

    # Korjaa ranget. 8-12 -> "8 viiva 12"
    viiva_numerot = re.findall(r"\b\d+-\d+\b", s)
    for v in viiva_numerot:
        s = s.replace(v, v.replace("-", " viiva "))
    
    s = s.replace(" klo ", " kello ")
    s = s.replace("m/s", "metriä sekunnissa")

    # korjaa numerot
    def replace_number(match):
        number = int(match.group(0))
        return numero_tekstiksi(number)

    s = re.sub(r"\d+", lambda x: replace_number(x), s)
    return s

def get_saatiedotus(driver):
    saatiedotus_url = "https://www.ilmatieteenlaitos.fi/saatiedotus-merenkulkijoille"
    driver.get(saatiedotus_url)

    soup = BeautifulSoup(driver.page_source, features="html5")
    saatiedotus_string = soup.select("div[id^=proxyId_6mddLTaDJSXFZjHemVsl61]")[0].text
    
    return saatiedotus_cleaner(saatiedotus_string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--asema_file", type=str, required=True)

    args = parser.parse_args()

    with open(args.asema_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    short2value = {x.split(",")[0].strip(): x.split(",")[1].strip() for x in lines}


    driver = webdriver.Chrome()
    # Säätiedotus merenkulkijoille

    saatiedotus_str = get_saatiedotus(driver)
    with open("out_01_saatiedotus_merenkulkijoille.txt", "w", encoding="utf-8") as f:
        f.writelines(saatiedotus_str)
    print(saatiedotus_str)

    # Sää rannikkoasemilla
    pbar = tqdm(short2value.keys())
    with open("out_02_saa_rannikkoasemilla.txt", "w", encoding="utf-8") as f:
        for i, asema in enumerate(pbar):
            aikaleima_str, asema_str = rannikkoasema_pipeline(driver, asema)
            if i == 0:
                f.write(f"Sää rannikkoasemilla tänään kello {aikaleima_str}.\n")
            
            f.write(f"{asema}: {asema_str.strip()}.\n")
            pbar.set_description(f"{asema}: {asema_str.strip()}")
            sleep(1)