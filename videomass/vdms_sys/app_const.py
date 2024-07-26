# -*- coding: UTF-8 -*-
"""
Author:  Werner F. Bruhin
Purpose: Application constants
Created: 06/04/2012

Edited by Gianluca (jeanslack) Pernigotto
Update: July 17 2024

Visit the complete list of the wx.Language CONSTANT identifiers at:
<https://docs.wxpython.org/wx.Language.enumeration.html#wx-language>
"""

import wx

# language domain
langDomain = "videomass"

# The wx.Language identifiers of the locale are COSTANTS rappresenting
# `int` objects, e.g wx.LANGUAGE_CZECH is 150 and wx.LANGUAGE_CZECH_CZECHIA
# is 151, ecc.
supLang = {  # languages you want to support.
    "Default": (wx.LANGUAGE_DEFAULT, ("System default language")),
    "ar_SA": (wx.LANGUAGE_ARABIC_SAUDI_ARABIA, ("Arabic (Saudi Arabia)")),
    "zh_CN": (wx.LANGUAGE_CHINESE_SIMPLIFIED, ("Chinese (simplified)")),
    "cs_CZ": (wx.LANGUAGE_CZECH_CZECHIA, ("Czech (Czechia)")),
    "nl_NL": (wx.LANGUAGE_DUTCH, ("Dutch")),
    "en_US": (wx.LANGUAGE_ENGLISH_US, ("English (United States)")),
    "fr_FR": (wx.LANGUAGE_FRENCH, ("French")),
    "de_DE": (wx.LANGUAGE_GERMAN, ("German (Germany)")),
    "hu_HU": (wx.LANGUAGE_HUNGARIAN_HUNGARY, ("Hungarian (Hungary)")),
    "it_IT": (wx.LANGUAGE_ITALIAN, ("Italian")),
    "pt_BR": (wx.LANGUAGE_PORTUGUESE_BRAZILIAN, ("Portuguese (Brazilian)")),
    "ru_RU": (wx.LANGUAGE_RUSSIAN, ("Russian")),
    "es_ES": (wx.LANGUAGE_SPANISH, ("Spanish (Spain)")),
    "es_MX": (wx.LANGUAGE_SPANISH_MEXICAN, ("Spanish (Mexico)")),
    "es_CU": (wx.LANGUAGE_SPANISH_CUBA, ("Spanish (Cuba)")),
}
