## ADD SUPPORT FOR NEW LANGUAGE

### Requirements
- [GNU gettext](https://www.gnu.org/software/gettext) (To build `.pot` and the `.mo` files)
- poEdit: to do the actual translation I recommend [poEdit](https://poedit.net/), it allows you to create or update a translation catalog (.po file) from the .pot file.
- Some kind of text editor to edit some code (notepad++, nano, etc are sufficient)
- [Git](https://git-scm.com/downloads)

### Notes
##### The instructions below assume basic knowledge of the command line (OS independent)

### Start

- To start a new translation, make sure you have the sources for the latest videomass release that you can download [here](https://github.com/jeanslack/Videomass/releases).

- Extract the archive.

- Browse the new folder and create two new folders inside /Videomass-?.?.?/locale path (for example create a 'de_DE' folder and within which a 'LC_MESSAGES' folder for the German 
language support) with the following tree:

    /Videomass
        /locale
            /de_DE
                /LC_MESSAGES
                
- Copy the **videomass.pot"** file translation template located in the '/locale' 
folder, and paste into the 'LC_MESSAGES' folder.

- rename it to change extension name to "videomass.po" . 

- Now open the "videomass.po" with a translation editing program, for example 
'PoEdit', and start your translation.

- You can close and resume your work whenever you want but you must always save your changes. This generates a file called 'videomass.mo' with your 
new native language tanslation.

- Before try your new translation by starting Videomass, open 'Videomass-?.?.?/videomass3/vdms_SYS/app_const.py' module with your favorite text-editor and append the newly 
translated language line, for example:

    "de": wx.LANGUAGE_GERMAN,
    
to:

    supLang = {"en": wx.LANGUAGE_ENGLISH,
               "it": wx.LANGUAGE_ITALIAN,
               "de": wx.LANGUAGE_GERMAN,
               }
- For a list of the supported languages to append on 'app_const.py', please see [wx.Language](https://wxpython.org/Phoenix/docs/html/wx.Language.enumeration.html#wx-language)

- When finish save 'app_const.py'.

- Try your new tranlation by open a terminal window, go to the 'Videomass-?.?.?' sources folder and type: 

      python3 launcher

When you have completed your translation with 'PoEdit', please send me your 'videomass.po' file at:

<jeanlucperni@gmail.com>

I will be grateful!!
