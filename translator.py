import os
import time

import pandas as pd
from google.cloud import translate
from googletrans import Translator
from rich import print

import openai
import openai_keys

OPENING_QUOTES = ["「", "『", "【", "（", "［", "《", "〈", "〔", "｛", "〖", "〘", "〚", "〝"]
CLOSING_QUOTES = ["」", "』", "】", "）", "］", "》", "〉", "〕", "｝", "〗", "〙", "〛", "〞"]

def translate_openai(desc):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "A chat between an user and an artificial intelligence assistant, "
                        "specialized in translation from japanese to english. The user inputs "
                        "some text in japanese, and the assistant responds simply with the translation "
                        "to english, and waits for the next input. The assistant tries to be succinct "
                        "since there is a space limit."},
            {"role": "user", "content": desc},
        ]
    )
    return completion.choices[0].message['content']

def translate_google_cloud(text, project_id="xeupiu"):
    client = translate.TranslationServiceClient()
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"

    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": "ja",
            "target_language_code": "en-US",
        }
    )

    return response.translations[0].translated_text

def translate_text(text, backend="google_cloud"):
    if not text:
        return ""

    if text[0] in OPENING_QUOTES:
        if text[-1] not in CLOSING_QUOTES:
            text = text[1:] # Remove opening quote

    if backend == "google_cloud":
        translated_text = translate_google_cloud(text)
    elif backend == "openai":
        translated_text = translate_openai(text)
    else:
        raise Exception(f"Unknown backend: {backend}")

    translated_text = translated_text.replace("``", "\"")
    translated_text = translated_text.replace("''", "\"")
    return translated_text

def should_translate_text(text):
    if text == "":
        return False
    if len(text) == 1:
        return False
    return True

if __name__ == "__main__":
    txt_jp = "伊集院って、あの金持ちのか．．．。嫌なクラスになっちまったなぁ。"

    print(f"Google Cloud:")
    txt_en = translate_google_cloud(txt_jp, "xeupiu")
    print(txt_en)