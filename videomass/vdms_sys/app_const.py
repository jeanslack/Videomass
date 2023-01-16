# -*- coding: UTF-8 -*-
# Author:  Werner F. Bruhin
# Purpose: Application constants
# Created: 06/04/2012
#
# Edited by Gianluca (jeanslack) Pernigotto
# Update: January 16 2023

# NOTE for translators: when you add new languages you
# also add them to "langnames"
# please refers to
# <https://docs.wxpython.org/wx.Language.enumeration.html#wx-language>
# for new supported languages.

import wx

# language domain
langDomain = "videomass"

# languages you want to support
supLang = {
    "Default": (wx.LANGUAGE_DEFAULT, ("System default language")),
    "zh_CN": (wx.LANGUAGE_CHINESE_SIMPLIFIED, ("Chinese (simplified)")),
    "nl_NL": (wx.LANGUAGE_DUTCH, ("Dutch")),
    "en_US": (wx.LANGUAGE_ENGLISH_US, ("English (United States)")),
    "fr_FR": (wx.LANGUAGE_FRENCH, ("French")),
    "it_IT": (wx.LANGUAGE_ITALIAN, ("Italian")),
    "pt_BR": (wx.LANGUAGE_PORTUGUESE_BRAZILIAN, ("Portuguese (Brazilian)")),
    "ru_RU": (wx.LANGUAGE_RUSSIAN, ("Russian")),
    "es_ES": (wx.LANGUAGE_SPANISH, ("Spanish")),
    "es_MX": (wx.LANGUAGE_SPANISH_MEXICAN, ("Spanish (Mexico)")),
}
