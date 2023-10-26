import time
import PIL.Image

from manga_ocr import MangaOcr

mocr = MangaOcr()

img = PIL.Image.open('data/caso_2/text_1.png')
text = mocr(img)
print(text)

img = PIL.Image.open('data/caso_2/text_2.png')
text = mocr(img)
print(text)

img = PIL.Image.open('data/caso_2/text_3.png')
text = mocr(img)
print(text)
