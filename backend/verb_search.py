from bs4 import BeautifulSoup
import requests

base_url = "https://www.translate.ru/спряжение%20и%20склонение/испанский/ir"

def download_html(url, file_name):
    req = requests.get(url)
    with open(f"pages/{file_name}.html", "wb") as f:
        f.write(req.content)

def get_info(verb):
    http_req = requests.get(f"https://www.translate.ru/спряжение%20и%20склонение/испанский/{verb}").text

    soup = BeautifulSoup(http_req, 'lxml')
    indicative = soup.find('div', class_='indicative text-center main-mode')

    tense_dict = {}
    
    for tense in indicative.find_all("span", class_="indicativo"):
        conjugation_list = []
        for con in tense.find_all("span"):
            conjugation_list.append(con.find("f").text)
        tense_dict[tense.find('b').text] = conjugation_list

    return tense_dict
