# Project XEUPIU

https://github.com/vgarciasc/xeupiu/assets/13024544/edc86216-9c61-4285-8f33-22b02235a9cf

## What is this?

This is an attempt to translate "Tokimeki Memorial: Forever With You" (1994, PS1), which has defied translation until now.

## Why is this?

Like many others, I saw Tim Rogers' review of Tokimeki Memorial a few years ago and was filled with a desire to play the game. However, also like many others, I was frustrated to discover that there was no translation of the game yet -- apparently the most popular version of the game ("Tokimeki Memorial: Forever With You") is very difficult to reverse engineer due to the way it's programmed. In the two years since, a community translation of the Super Famicom version has been made (as it is easier to hack), but many, like myself, have avoided playing this version because it pales in comparison to the more premium "Forever With You" version (which is fully voiced and runs at 60 FPS, for example).

This project is an attempt to fill this gap. **"Project XEUPIU"** is a translation tool for Tokimeki Memorial: Forever With You" which reads the text output by the game, processes it, and displays the translated text in a window that overlays the game text. As such, it is not a traditional "reverse engineering" translation which edits the game's files and code, but is in fact closer to approaches like that of Textractor.

## How does this differ from Textractor?

The main differences between what I'm doing and other tools like Textractor are that:
- **Perfect character detection rate**: Since the game runs on an emulator (a PS1 emulator in my case), it is difficult to get a text hooker, which means tools like Textractor cannot be used. Another solution would involve using OCR; however, this introduces possible errors, since OCR can make mistakes. In the program I'm proposing, text is detected by matching each character visually using the font displayed in the character naming screen, which has a 100% success rate.
- **No need for terrible machine translation**: Textractor (and similar tools) relies on machine translation. The tool I'm proposing uses a mix of human and machine translations: basically, each time a text appears on the screen, the program searches its database to see if this line exists. If it does, the corresponding translation is displayed; if it doen't, then it is translated using machine translation. Since the database can be edited by anyone, theoretically if the database is complete there would be no need for machine translation at all.

In other words, this works, while Textractor doesn't; moreover, even if Textractor worked, it is better than Textractor because it allows for human expert translations.

## What does the database look like?

It's a CSV, like [this](https://github.com/vgarciasc/xeupiu/blob/main/data/texts/database_text.csv). Perhaps in the future it will be necessary to add more metadata, but for now it's quite simple, as you'll see. The file can be easily edited by competent translators, shared online, and future players who download this file will be able to interact with a high-quality translation, instead of a machine one.

## Can I already play this?

The tool is completely playable with machine translation, but human translation is still in progress. A tutorial on how to set it up can be found [here](tutorial.md).

## How can I help?

As I envision it, the project is composed of three phases:

1. **Programming**: developing the translation tool and making it work with the game.
2. **Database creation**: creating a database of all the text in the game.
3. **Translation**: translating the database.

As most of the base programming is already done, we are currently moving from phase 1 to phase 2.
This means that we need people to play through the game using the tool, so that we can both (1) populate
the game's script database, and (2) find any bugs with the tool. Since the script is not done yet, all translation
during this phase needs to be done using machine translation (we suggest DeepL since it's free and high-quality).
If you are interested in helping with this, please reach out to `tokimemo (at) vinizinho (dot) net`!

## Is this specific to Tokimeki Memorial: Forever With You?

There are several things in the current implementation that are specific to this game, since specific information 
allows us to create a more customized, high-quality translation experience. 
However, the overall approach can surely be ported to other games.
