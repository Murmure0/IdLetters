from transformers import pipeline
import json
import requests
import time

# DICT LANGUAGE TO TRANSLATE TO ----------------------------------------------------------

lang_dict = {
    "fr" : "french",
    "en" : "english"
}

# INIT CONFIG : you need a huggingFace token to make a call API --------------------------

def load_config(file_path):
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    api_token = config.get('api_token')
    return api_token

# LANGUAGE DETECTION ---------------------------------------------------------------------

def API_call_detect_lang(input_text):
    API_URL = "https://api-inference.huggingface.co/models/papluca/xlm-roberta-base-language-detection"
    token = load_config("config.json")
    headers = {"Authorization": f"Bearer {token}"}
    print(token)
    payload = {"text" : input_text}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

def detec_lang(input_text):
    response = API_call_detect_lang(input_text)
    if response.status_code != 200:
        time.sleep(20)    
    response = API_call_detect_lang(input_text)
    return response.json()

# TRADUCTION ---------------------------------------------------------------------

def API_call_trad(text_to_trad,from_lang, to_lang):
    API_URL = f"https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-{from_lang}-{to_lang}"
    token = load_config("config.json")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs" : text_to_trad}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

def make_trad(text_to_trad,from_lang, to_lang):
    response = API_call_trad(text_to_trad,from_lang, to_lang)
    if response.status_code != 200:
        time.sleep(20)    
    response = API_call_trad(text_to_trad,from_lang, to_lang)
    return response.json()
