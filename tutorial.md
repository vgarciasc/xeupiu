# Running XEUPIU

## How to install

### Setting up the emulator

1. Download the [latest version of the DuckStation emulator ](https://www.duckstation.org/) (latest version tested: 0.1-6759-gc015039a (dev))
2. Install the emulator and set it up with your PSX BIOS
3. Download the Tokimeki Memorial - Forever With You (Rev 4) ROM in Japanese
4. Configure the emulator by accessing Settings -> Graphics and changing:
	1. Aspect ratio: 4:3
	2. Crop: All Borders
	3. Scaling: Nearest Neighbor (Integer)

### Setting up the translation backend

The game is already playable, but the game script has not been fully collected yet, which means that only machine translation works for now. This tool supports machine translation via Google Translate, OpenAI's GPT, or DeepL. If you don't have a key for one of these services, I suggest using DeepL, since it is free and easy to set up:

1. Go to [DeepL's website](https://www.deepl.com/en/pro-api?cta=header-pro-api)
2. Sign up for free (credit card required)
3. Go to the [Keys panel](https://www.deepl.com/your-account/keys)
4. Copy your API key

### Setting up the translation system

1. Download the latest XEUPIU tool release [here](https://github.com/vgarciasc/xeupiu).
2. Unzip it somewhere.
3. Start up the game in DuckStation.
4. Once you're at the game's title screen, press START.
5. Open the XEUPIU tool by double-clicking on `xeupiu.exe`.
6. Fill the empty fields with your DeepL API Key, desired player character name, surname, and nickname.
7. Follow the on-screen instructions.
8. Enjoy!

## Frequently Asked Questions

### 1. The overlays are being shown even when the game is minimized!

I'm aware of this issue, however it's low priority right now. For the time being, I suggest simply closing the tool when you are not playing the game, to make the overlays go away.

### 2. I moved the game screen, but the overlays did not follow!

Just as above: I are aware of this issue, however it's low priority right now. Please maintain the game screen in the same position after opening the tool; if you want to change its position, simply close the tool and reopen it again.

### 3. During phone conversations, the textbox overlay disappears after choosing which girl to get info on!

Most probable cause is that the cursor became free-form. Please move it outside the textbox so it can be correctly detected.

### 4. I have set up the tool correctly, but when I try to run it, it crashes immediately!

There are some known Windows configurations that affect the tool in its current form; we are working on fixing this for future versions. In the meantime, before opening the tool, please guarantee that:

1. Your Windows "scale and layout" is set to 100%.
2. You are currently only using one monitor.

If these items are true for your PC but the tool keeps crashing, read on.

### 5. The tool was working well, but now when I try to open it, it crashes immediately!

This is a known issue with the Windows internal screenshotting API. Please do the following:

1. Close both XEUPIU and the emulator.
2. Close other windows in your computer.
3. Reopen XEUPIU and the emulator.

If this does not solve your issue, read on.

### 6. The game crashed and I don't know why!

If none of the questions above apply to your case, please reach out on the [Discord server](https://discord.gg/aH5meFKRB7). I am only one person with a busy job so I apologize upfront if I take a while to answer.
