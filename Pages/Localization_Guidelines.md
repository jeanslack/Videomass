---
layout: default
title: Translate Videomass Offline
parent: Contribute
nav_order: 1
---

# Localization Guidelines

Help to translate Videomass to other languages
{: .fs-6 .text-grey-dk-100}
-----------------

## Updates an existing translation
{: .bg-green-300}

#### Requirements:
- [GNU gettext](https://www.gnu.org/software/gettext), to build `.mo` file.
- [poEdit](https://poedit.net/), to do the actual translation I recommend poEdit, 
it allows you to create or update a translation catalog, for instance, a `.po` file from 
a `.pot` file.

> There is a bit of difference between [.po file format (portable object)](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) 
> and [.pot file format (portable object template)](https://help.phrase.com/help/gettext-template-pot-files). 
> Specifically, the [videomass.pot](https://github.com/jeanslack/Videomass/blob/master/videomass3/locale/videomass.pot) 
> file is just a template that contains the new strings not yet translated and should 
> never be modified directly. The [videomass.po](https://github.com/jeanslack/Videomass/blob/master/videomass3/locale/it_IT/LC_MESSAGES/videomass.po) 
> file can instead be edited for translation or updated with the latest strings 
> not yet translated, i.e. by importing `videomass.pot` file (see below).
{: .text-grey-dk-100}

#### Let's go

- Download [latest](https://github.com/jeanslack/Videomass/releases/latest) release of Videomass

- Extract the archive and navigate inside the obtained folder.

- Browse into the `videomass3/locale` folder, then choose the language folder to translate.

- Locate `videomass.po` file related to your language, example:

``` text
    Videomass(rootdir)
    |__ videomass3
        |__ locale
            |__ it_IT
                |__ LC_MESSAGES
                    |__ videomass.po
```
- Open the `videomass.po` file with [poEdit](https://poedit.net/) 

- Click on [poEdit](https://poedit.net/) menu bar *-> Catalog -> Update from POT file...*, then 
import the `videomass.pot` file template sited on `locale` folder. This is **important** as it 
ensures that the `videomass.po` file is fully updated with the latest translation strings.

- Also, check the catalog property data on menu bar *> Catalog > Property...*
and make sure it contains at least some updated information you could provide.

- Now, you are ready to start your translation. When you're done save your work; 
you can always resume your work from where you left off.

- Before running Videomass to test your updated translation, Make sure 
[Python3](https://www.python.org/), [wxPython](https://www.wxpython.org/), 
[PyPubSub](https://pypubsub.readthedocs.io/en/v4.0.3/), [requests](https://docs.python-requests.org/en/master/) 
and [youtube-dl](https://youtube-dl.org/) are installed. Visit the Videomass 
[wiki](https://github.com/jeanslack/Videomass/wiki/Installing-and-Dependencies) 
page for installation details. 

- Try your new tranlation by open a terminal window, `cd` on the `Videomass` 
sources folder and type: `python3 launcher`. 

When you have completed your translation with 'PoEdit', please [Create a pull 
request](https://github.com/jeanslack/Videomass/pulls) or send me your 
`videomass.po` file at: <jeanlucperni@gmail.com>   

I will be grateful!!

At your disposal for clarification.

## Start with a new translation
{: .bg-green-300}

If you are not familiar with the command line and some applications described below, STOP! 
Contact me and describe me in which language you want to translate Videomass. I will provide 
everything you need, so that you can only open [poEdit][poEdit](https://poedit.net/) 
and start your new translation. 

#### Requirements
- [GNU gettext](https://www.gnu.org/software/gettext) (To build `.pot` and the 
`.mo` files)
- [poEdit](https://poedit.net/), to do the actual translation I recommend poEdit, 
it allows you to create or update a translation catalog, for instance, a `.po` file from 
a `.pot` file.
- Some kind of text editor to edit some code (notepad++, nano, Mousepad etc are sufficient)
- [Git](https://git-scm.com/downloads), to clone the latest Videomass snapshot (optionally).

> Note: The instructions below assume basic knowledge of the command line (OS independent)
{: .fs-4 .text-grey-dk-100}

- To start a new translation, clone videomass with git command: `git clone https://github.com/jeanslack/Videomass.git`

- Or download [here](https://github.com/jeanslack/Videomass/archive/refs/heads/master.zip) latest Videomass snapshot, then unzip the archive.

- In this example we assume that the new language to be translated is **German**. 

- Then, browse the new Videomass folder and create two new folders: `de_DE` folder 
and within which a `LC_MESSAGES` folder, like following tree:

```text
    Videomass(rootdir)
    |__ videomass3
        |__ locale
            |__ de_DE
                |__ LC_MESSAGES
```
                
- Copy the `videomass.pot` file translation template located in the `/locale` 
folder, and paste into the `LC_MESSAGES` folder.

- Rename it to change extension name to `videomass.po` . 

- Now open the `videomass.po` with [poEdit](https://poedit.net/), check the catalog 
property data on menu bar *> Catalog > Property...* and make sure it contains at least 
some updated information you could provide.

- Now, you are ready to start your new translation. When you're done save your work; 
you can always resume your work from where you left off. This generates (compile) a file called 
`videomass.mo` with your new native language tanslation.

- Before running Videomass to test your new translation, Make sure 
[Python3](https://www.python.org/), [wxPython](https://www.wxpython.org/), 
[PyPubSub](https://pypubsub.readthedocs.io/en/v4.0.3/), [requests](https://docs.python-requests.org/en/master/) 
and [youtube-dl](https://youtube-dl.org/) are installed. Visit the Videomass 
[wiki](https://github.com/jeanslack/Videomass/wiki/Installing-and-Dependencies) 
page for installation details. 

- Open the `Videomass/videomass3/vdms_SYS/app_const.py` file with your favorite 
text-editor and append the newly translated language line, for example:

```python
    "de": wx.LANGUAGE_GERMAN,
```

to:

```python
    supLang = {"en": wx.LANGUAGE_ENGLISH,
               "it": wx.LANGUAGE_ITALIAN,
               "de": wx.LANGUAGE_GERMAN,
               }
```

- For a list of the supported languages to append on `app_const.py`, please see 
[wx.Language](https://wxpython.org/Phoenix/docs/html/wx.Language.enumeration.html#wx-language)

- When finish save `app_const.py` .

- Try your new tranlation by open a terminal window, `cd` on the `Videomass` 
sources folder and type: `python3 launcher`

When you have completed your new translation, please [Create a pull 
request](https://github.com/jeanslack/Videomass/pulls) or send me your 
`videomass.po` file at: <jeanlucperni@gmail.com> 

I will be grateful!!
