# Help translate videomass to other languages
-----------------

### Requirements
- [GNU gettext](https://www.gnu.org/software/gettext) (To build `.pot` and the 
`.mo` files)
- [poEdit](https://poedit.net/): to do the actual translation I recommend poEdit, 
it allows you to create or update a translation catalog (.po file) from the .pot file.
- Some kind of text editor to edit some code (notepad++, nano, Mousepad etc are sufficient)
- [Git](https://git-scm.com/downloads)

> <ins>**Note:**</ins>
>
> The instructions below assume basic knowledge of the command line (OS independent)

### Updates an existing translation
Over time, new releases of Videomass could include new text strings not yet 
translated. To update an existing translation follow these steps:

- Clone videomass with git command:
```
git clone https://github.com/jeanslack/Videomass.git
```

- Otherwise, if you have not git, download it as zip archive:
Click on to 'Clone' button on [https://github.com/jeanslack/Videomass] and
choose 'Download ZIP'.

- Browse into the `videomass3/locale` folder package by searching for the 'videomass.po' 
file related to the language to be translated, example:
``` Videomass base directory
        /videomass3
            /locale
                /de_DE
                    /LC_MESSAGES
                        videomass.po
```

- Open the "videomass.po" with 'PoEdit' and go to menu bar > Catalog > 
Update from POT file...   
Browse on `locale` folder where there is a videomass.pot file template and 
select it, then open catalog template. This serves to update current videomass.po 
file at the latest features.

- Check the catalog property data on menu bar > Catalog > Property... 
and make sure it contains at least some information. Otherwise you could provide 
it here.

- Now, you are ready to start your translation. When you're done save your work; 
you can always resume your work from where you left off.

- Try your new tranlation by open a terminal window, go to the 'Videomass-?.?.?' 
sources folder and type:   

      `python3 launcher`

When you have completed your translation with 'PoEdit', please send me your 
'videomass.po' file at: <jeanlucperni@gmail.com>   

I will be grateful!!

### Start with a new translation

- To start a new translation, clone videomass with git command:
```
git clone https://github.com/jeanslack/Videomass.git
```

- Browse the new Videomass folder and create two new folders inside 
`/Videomass-?.?.?/locale` path (for example create a `de_DE` folder and within 
which a `LC_MESSAGES` folder for the German language support) with the following tree:
```
    Videomass base directory
        /videomass3
            /locale
                /de_DE
                    /LC_MESSAGES
```
                
- Copy the **videomass.pot"** file translation template located in the `/locale` 
folder, and paste into the `LC_MESSAGES` folder.

- rename it to change extension name to `videomass.po` . 

- Now open the `videomass.po` with a translation editing program, for example 
'PoEdit', and start your translation.

- Check the catalog property data on menu bar > Catalog > Property... 
and make sure it contains at least some information. Otherwise you could provide 
it here.

- You can close and resume your work whenever you want but you must always save 
your changes. This generates a file called `videomass.mo` with your new native 
language tanslation.

- Before try your new translation by starting Videomass, open the 
`Videomass-?.?.?/videomass3/vdms_SYS/app_const.py` module with your favorite 
text-editor and append the newly translated language line, for example:
```
    "de": wx.LANGUAGE_GERMAN,
```
to:
```
    supLang = {"en": wx.LANGUAGE_ENGLISH,
               "it": wx.LANGUAGE_ITALIAN,
               "de": wx.LANGUAGE_GERMAN,
               }
```
- For a list of the supported languages to append on `app_const.py`, please see 
[wx.Language](https://wxpython.org/Phoenix/docs/html/wx.Language.enumeration.html#wx-language)

- When finish save `app_const.py` .

- Try your new tranlation by open a terminal window, go to the `Videomass-?.?.?` 
sources folder and type: 

      `python3 launcher`

When you have completed your translation with 'PoEdit', please send me your 
`videomass.po` file with language description at:

<jeanlucperni@gmail.com>

I will be grateful!!
