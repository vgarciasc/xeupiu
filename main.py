import time
import PIL.Image

from manga_ocr import MangaOcr
from screenshot import capture_pixels

mocr = MangaOcr()

# img = PIL.Image.open('data/ss4.png')
for i in range(10000):
    img = capture_pixels("VLC")
    img = img.crop((65, 420, 65 + 520, 420 + 105))
    text = mocr(img)

    #print with timestamp, miliseconds
    print(i, time.strftime("%H:%M:%S") + "." + str(int(round(time.time() * 1000))) + " " + text)