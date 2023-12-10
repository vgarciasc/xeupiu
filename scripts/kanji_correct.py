import glob
from PIL import Image

# The goal of this script is to migrate kanji from 'kanji_proposals/identified' and 'kanji_proposals/to_accept'
# to 'kanji_corrected'. This is because the kanji in 'kanji_proposals' do not match the ones in the character naming
# screen, which we think happens because the game's font is not exactly MS Gothic 11x11, but a prototypic version
# (< 2.3) that has been lost to time.

if __name__ == "__main__":
    for filename in glob.glob("data/characters/kanji_proposals/identified/*.png") + \
                    glob.glob("data/characters/kanji_proposals/to_accept/*.png"):
        img = Image.open(filename)
        img = img.resize((img.width // 2, img.height // 2), Image.NEAREST)
        img = img.crop((2, 2, 2 + 11, 2 + 11))

        # save image to kanji_corrected/
        _f = filename.split('/')[-1].split('\\')[-1]
        img.save(f"data/characters/kanji_corrected/{_f}")

