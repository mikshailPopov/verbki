import json
import os


def get_all_languages_with_tenses(path:str) -> dict:
    with open(path, 'r', encoding="utf-8") as file:
        languages = json.load(file)
    return languages

def get_all_deck_paths():
    with open('backend/configs/paths.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['deck_paths']

def add_new_deck_path(new_path):
    with open('backend/configs/paths.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["deck_paths"].append(new_path)

    with open('backend/configs/paths.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)


def remove_deck_path(path):
    with open(os.path.join(os.getcwd(),'backend/configs/paths.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    try:
        data["deck_paths"].remove(path)
    except Exception as e:
        print(e)

    with open(os.path.join(os.getcwd(),'backend/configs/paths.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f)
