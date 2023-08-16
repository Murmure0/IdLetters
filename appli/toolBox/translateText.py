from transformers import pipeline

# def create_model(from_lang, to_lang):
#     # from_lang = "en"
#     # to_lang = "fr"
#     task_to_do = f"translation_{from_lang}_to_{to_lang}"
#     model_to_import = f"Helsinki-NLP/opus-mt-{from_lang}-{to_lang}"
#     return pipeline(task_to_do, model=model_to_import)
# App
# API
import json
import requests

def load_config(file_path):
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    api_token = config.get('api_token')
    return api_token


def API_call(text_to_trad,from_lang, to_lang):
    API_URL = f"https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-{from_lang}-{to_lang}"
    token = load_config("config.json")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs" : text_to_trad}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def make_trad(text_to_trad,from_lang, to_lang):
    ret = API_call(text_to_trad,from_lang, to_lang)
    return ret
    # model = create_model(from_lang, to_lang)
    # translated_txt = model(text_to_trad)
    # return translated_txt[0]['translation_text']

def detec_lang(input_text):
    model = pipeline(model="papluca/xlm-roberta-base-language-detection") # >1Go : super lourd
    detected_lang = model(input_text)
    return detected_lang[0]['label']