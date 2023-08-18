from transformers import pipeline
import json
import requests
import time

# DICT LANGUAGE TO TRANSLATE TO ----------------------------------------------------------

lang_dict = {
    "fr" : "french",
    "en" : "english",
    "de" : "german",
    "es" : "spanish",
    "nl" : "dutch",
    "pl" : "polish",
}

# Languages we could identify / could make the traduction :
# arabic (ar), 
# bulgarian (bg),
# german (de), /        OK
# modern greek (el), 
# english (en), /       OK
# spanish (es), /       OK
# french (fr), /        OK
# hindi (hi), 
# italian (it), /       ok : it/fr-en-de-es; en-de-es-/it 
# japanese (ja), 
# dutch (nl), /         ok :nl/fr; nl/en; nl/es; en/nl; de/nl; es/nl || pas ok : nl/de, fr/nl
# polish (pl),          ok : pl/fr-en-de-es; fr-de-es/pl || pas ok : pl/nl; en-nl/pl
# portuguese (pt), 
# russian (ru), 
# swahili (sw), 
# thai (th), 
# turkish (tr), 
# urdu (ur), 
# vietnamese (vi),
# chinese (zh)


## + Pipeline models ------------------------------------------------------------------------
## Load the model tu use it localy : no information sent through internet, but slower than API

# LANGUAGE DETECTION ---------------------------------------------------------------------
def detect_lang_ppl(input_text):
    classificator = pipeline("text-classification",
                    model='papluca/xlm-roberta-base-language-detection')
    dict_langs_found = classificator(input_text)
    lang = dict_langs_found[0]['label']
    return lang

def make_trad_ppl(text_to_trad,from_lang, to_lang):

    if not(from_lang in lang_dict) or not(to_lang in lang_dict):
        ok_languages = ",".join(lang_dict.keys())
        return f"You ask for a translation from {from_lang} to {to_lang}\nWe accept the following languages: {ok_languages}"
    translator = pipeline(f"translation_{from_lang}_to_{to_lang}",
                model=f"Helsinki-NLP/opus-mt-{from_lang}-{to_lang}")
    dict_transl_txt = translator(text_to_trad)
    transl_txt = dict_transl_txt[0]['translation_text']
    return transl_txt

## + API with huggingFace ------------------------------------------------------------------
# Faster but only a Free tier: 30k Total Characters --------------------------------------
# Find your token : https://huggingface.co/settings/tokens -------------------------------
# Check your usage : https://api-inference.huggingface.co/dashboard/ ---------------------

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

def detec_lang_API(input_text):
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

def make_trad_API(text_to_trad,from_lang, to_lang):
    response = API_call_trad(text_to_trad,from_lang, to_lang)
    if response.status_code != 200:
        time.sleep(20)    
    response = API_call_trad(text_to_trad,from_lang, to_lang)
    return response.json()
