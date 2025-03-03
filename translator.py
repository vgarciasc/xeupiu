import os

from google.cloud import translate
from config import CONFIG

import openai
import deepl

from constants import format_translated_text
from database import Database

OPENING_QUOTES = ["「", "『", "【", "（", "［", "《", "〈", "〔", "｛", "〖", "〘", "〚", "〝"]
CLOSING_QUOTES = ["」", "』", "】", "）", "］", "》", "〉", "〕", "｝", "〗", "〙", "〛", "〞"]

openai.organization = CONFIG["translation"]["openai"]["organization"]
openai.api_key = CONFIG["translation"]["openai"]["api_key"]

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CONFIG["translation"]["google_cloud"]["credential_path"]

class Translator():
    def __init__(self):
        self.backend = CONFIG["translation"]["backend"]
        self.deepl_model = None

    def translate_openai(self, desc):
        completion = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system",
                 "content": "A chat between an user and an artificial intelligence assistant, "
                            "specialized in translation from japanese to english."},
                {"role": "user", "content": desc},
            ]
        )
        print(f"Tokens used: {completion.usage.total_tokens}")
        return completion.choices[0].message['content']

    def translate_google_cloud(self, text, project_id="xeupiu"):
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

    def translate_deepl(self, text):
        if CONFIG["translation"]["deepl"]["api_key"] == "" or CONFIG["translation"]["deepl"]["api_key"] is None:
            # raise Exception("DeepL API key is not set.")
            print("WARNING: DeepL API key is not set. Returning japanese text.")
            return text

        if self.deepl_model is None:
            self.deepl_model = deepl.Translator(auth_key=CONFIG["translation"]["deepl"]["api_key"])

        return self.deepl_model.translate_text(text, source_lang="JA", target_lang=CONFIG["translation"]["lang"]).text

    def translate(self, text, backend=None):
        if not text:
            return ""

        text_to_translate = text
        if text[0] in OPENING_QUOTES and text[-1] not in CLOSING_QUOTES:
            text_to_translate = text[1:] # Remove opening quote

        text_to_translate, date_jp = Database.generalize_date(text_to_translate)

        if not backend:
            backend = CONFIG["translation"]["backend"]

        if backend == "google_cloud":
            translated_text = self.translate_google_cloud(text_to_translate)
        elif backend == "openai":
            translated_text = self.translate_openai(text_to_translate)
        elif backend == "deepl":
            translated_text = self.translate_deepl(text_to_translate)
        elif backend == "none":
            translated_text = text
        else:
            raise Exception(f"Unknown backend: {backend}")

        translated_text = format_translated_text(text, translated_text)

        return translated_text

    @staticmethod
    def should_translate_text(text):
        if text == "":
            return False
        if len(text) == 1:
            return False
        return True

if __name__ == "__main__":
    txt_jp = "伊集院って、あの金持ちのか．．．。嫌なクラスになっちまったなぁ。"
    tt = Translator()

    print(f"Google Cloud:")
    txt_en = tt.translate_google_cloud(txt_jp, "xeupiu")
    print(txt_en)

    print(f"OpenAI:")
    txt_en = tt.translate_openai(txt_jp)
    print(txt_en)

    print(f"DeepL:")
    txt_en = tt.translate_deepl(txt_jp)
    print(txt_en)