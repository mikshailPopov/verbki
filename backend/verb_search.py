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
    subjuntivo = soup.find('div', class_='subjuntivo text-center main-mode')
    imperativo = soup.find('div', class_='imperativo text-center main-mode')

    tense_dict = {}
    
    for tense in indicative.find_all("span", class_="indicativo"):
        conjugation_list = []
        for con in tense.find_all("span"):
            conjugation_list.append(con.find("f").text)
        tense_dict[f"Indicativo {tense.find('b').text.strip()}"] = conjugation_list

    for tense in subjuntivo.find_all("span", class_="subjuntivo"):
        conjugation_list = []
        for con in tense.find_all("span"):
            conjugation_list.append(con.find("f").text)
        tense_dict[f"Subjuntivo {tense.find('b').text.strip()}"] = conjugation_list

    for tense in imperativo.find_all("span", class_="imperativo"):
        conjugation_list = []
        for con in tense.find_all("span"):
            conjugation_list.append(con.find("value").text)
        tense_dict[f"Imperativo"] = conjugation_list

    return tense_dict

# download_html("https://conjugator.reverso.net/conjugation-spanish-verb-comer.html", "comer")

print(get_info("ir"))