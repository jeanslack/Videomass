# -*- coding: UTF-8 -*-
# Author:  Werner F. Bruhin
# Purpose: Application constants
# Created: 06/04/2012
#
# Edited by Gianluca (jeanslack) Pernigotto
# Update: June 29 2022

# NOTE for translators: when you add new languages you
# also add them to "langnames"
# please refers to
# <https://docs.wxpython.org/wx.Language.enumeration.html#wx-language>
# for new supported languages.

import wx

# language domain
langDomain = "videomass"
# languages you want to support
supLang = {"Default": wx.LANGUAGE_DEFAULT,
           "zh_CN": wx.LANGUAGE_CHINESE_SIMPLIFIED,
           "nl_NL": wx.LANGUAGE_DUTCH,
           "en_US": wx.LANGUAGE_ENGLISH_US,
           "it_IT": wx.LANGUAGE_ITALIAN,
           "pt_BR": wx.LANGUAGE_PORTUGUESE_BRAZILIAN,
           "ru_RU": wx.LANGUAGE_RUSSIAN,
           "es_ES": wx.LANGUAGE_SPANISH,
           "es_MX": wx.LANGUAGE_SPANISH_MEXICAN,
           }
# Make languages available to the preferences dialog
langnames = {"Default": ("System default language"),
             "zh_CN": ("Chinese (simplified)"),
             "nl_NL": ("Dutch"),
             "en_US": ("English (United States)"),
             "it_IT": ("Italian"),
             "pt_BR": ("Portuguese (Brazilian)"),
             "ru_RU": ("Russian"),
             "es_ES": ("Spanish"),
             "es_MX": ("Spanish (Mexico)"),
             }
