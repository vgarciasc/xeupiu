import glob
from PIL import Image

if __name__ == "__main__":
    for filename in glob.glob("data/characters/kanji_proposals/identified/*.png") + \
                    glob.glob("data/characters/kanji_proposals/to_accept/*.png"):
        img = Image.open(filename)
        img = img.resize((img.width // 2, img.height // 2), Image.NEAREST)
        img = img.crop((2, 2, 2 + 11, 2 + 11))

        # save image to kanji_corrected/
        _f = filename.split('/')[-1].split('\\')[-1]
        img.save(f"data/characters/kanji_corrected/{_f}")

