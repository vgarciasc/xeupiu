import os
import time

import pandas as pd
from rich import print

import openai
import openai_keys

def translate_jpn2eng(desc):
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


def should_translate_text(text):
    if text == "":
        return False
    if len(text) == 1:
        return False
    return True

if __name__ == "__main__":
    txt_jp = "伊集院、いないと思うが．．．。僕が理事長の孫の伊集院レイだ。"
    txt_en = translate_jpn2eng(txt_jp)
    print(txt_en)