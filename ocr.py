import time
import PIL.Image

from manga_ocr import MangaOcr

mocr = MangaOcr()

img = PIL.Image.open('data/ss4.png')
img = img.crop((60, 350, 580, 455))
text = mocr(img)
print(text)
