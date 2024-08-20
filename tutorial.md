## How to install

### Setting up the emulator

1. Download the [latest version of the DuckStation emulator ](https://www.duckstation.org/)(latest version tested: 0.1-6759-gc015039a (dev))
2. Install the emulator and set it up with your PSX BIOS
3. Download the Tokimeki Memorial - Forever With You (Rev 4) ROM in Japanese
4. Configure the emulator by accessing Settings -> Graphics and changing:
	1. Aspect ratio: 4:3
	2. Crop: All Borders
	3. Scaling: Nearest Neighbor (Integer)

### Setting up the translation backend

The game is already playable, but the game script has not been fully collected yet, which means that only machine translation works for now. Our tool supports machine translation via Google Translate, OpenAI's GPT, or DeepL. If you don't have a key for one of these services, we suggest using DeepL, since it is free and easy to set up:

1. Go to [DeepL's website](https://www.deepl.com/en/pro-api?cta=header-pro-api)
2. Sign up for free (credit card required)
3. Go to the [Keys panel](https://www.deepl.com/your-account/keys)
4. Copy your API key 
5. Open the `config.json` configuration file and paste your API key in the `deepl` > `api_key` field
6. Confirm that `translation` > `backend` is set up as "`deepl`"

### Setting up the translation system

1. Download the latest XEUPIU tool release [here](https://github.com/vgarciasc/xeupiu).
2. Unzip it somewhere.
3. Start up the game's ROM
4. Once you're at the game's title screen, press START.
5. Open the XEUPIU tool.
6. Enjoy!
