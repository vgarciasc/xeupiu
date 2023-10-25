import time
import PIL.Image

from manga_ocr import MangaOcr
from screenshot import get_window_by_title
from overlay import OverlayWindow

window = OverlayWindow(670, 480)
mocr = MangaOcr()

# img = PIL.Image.open('data/ss4.png')
for i in range(10000):
    img = get_window_by_title("gameplay_emerald.mp4")
    # img.save("data/tmp_window.png")
    img = img.crop((65, 385, 65 + 520, 385 + 105))
    text = mocr(img)
    # img.save("data/tmp_text.png")

    #print with timestamp, miliseconds
    print(i, time.strftime("%H:%M:%S") + "." + str(int(round(time.time() * 1000))) + " " + text)
    window.update(text)