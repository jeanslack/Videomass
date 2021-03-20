# Help to translate videomass to other languages
-----------------

### Updates an existing translation
The following languages have not yet been translated:   
- de_DE   (German)
- en_GB   (English)
- es_ES   (Spanish)
- fr_FR   (French)
- pl_PL   (Polish)   

You can choose the language you prefer to translate (even those not yet existing).

#### Requirements

[poEdit](https://poedit.net/): to do the actual translation I recommend poEdit, 
it allows you to create or update a translation catalog , for instance, a `.po` 
file from a `.pot` file.

> There is a bit of difference between **`.po`** file **(portable object)** and 
> **`.pot`** file **(portable object template)**. Specifically, the `videomass.pot` 
> file is just a template that contains the new strings not yet translated and should 
> never be modified directly. The `videomass.po` file can instead be edited for translation 
> or updated with the latest strings not yet translated, i.e. by importing `videomass.pot` 
> (see below).

#### Let's go

- Download latest release of Videomass from https://github.com/jeanslack/Videomass/releases

- Extract the archive and navigate inside the obtained folder.

- Browse into the `videomass3/locale` folder, then choose the language folder to translate.

- Browse on by searching for the 'videomass.po' file related to the language to be translated, example:

``` Videomass(base dir.)
    |__ videomass3
        |__ locale
            |__ de_DE
                |__ LC_MESSAGES
                    |__ videomass.po
```
- Open the "videomass.po" file with 'PoEdit' 

- Find for *> Catalog > Update from POT file...* on the poEdit menu bar, then 
import the `videomass.pot` file template sited on `locale` folder. This serves 
to update current `videomass.po` file at the latest features.

- Check the catalog property data by *> Catalog > Property...* of the poEdit menu bar 
and make sure it contains at least some information. Otherwise you could provide 
it.

- Now, you are ready to start your translation. When you're done save your work; 
you can always resume your work from where you left off.

When you have completed your translation with 'PoEdit', please [Create a pull 
request](https://github.com/jeanslack/Videomass/pulls) or send me your 
'videomass.po' file at: <jeanlucperni@gmail.com>   

I will be grateful!!

At your disposal for clarification.

### Start with a non-existent translation

If you are not familiar with the command line and some applications described below, STOP! 
Contact me and describe me in which language you want to translate Videomass. I will make 
all the necessary preparations myself, so that you can only open the application to do 
the translations and start your new translation. 

#### Requirements
- [GNU gettext](https://www.gnu.org/software/gettext) (To build `.pot` and the 
`.mo` files)
- [poEdit](https://poedit.net/): to do the actual translation I recommend poEdit, 
it allows you to create or update a translation catalog (.po file) from the .pot file.
- Some kind of text editor to edit some code (notepad++, nano, Mousepad etc are sufficient)
- [Git](https://git-scm.com/downloads)

> <ins>**Note:**</ins>
>
> The instructions below assume basic knowledge of the command line (OS independent)

- To start a new translation, clone videomass with git command:
```
git clone https://github.com/jeanslack/Videomass.git
```

- Browse the new Videomass folder and create two new folders inside 
`/Videomass-?.?.?/locale` path (for example create a `de_DE` folder and within 
which a `LC_MESSAGES` folder for the German language support) with the following tree:
```
    Videomass(rootdir)
    |__ videomass3
        |__ locale
            |__ de_DE
                |__ LC_MESSAGES
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
