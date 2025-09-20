
from __future__ import annotations

import base64
import collections
import csv
import datetime
import enum
import hashlib
import hmac as hmac_lib
import itertools
import json
import logging
import os
import re
import sys
import tempfile
import threading
import time
import traceback
import typing
import unicodedata
import warnings
import zlib
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, MutableMapping, MutableSet, Reversible
from contextlib import ContextDecorator, contextmanager
from difflib import HtmlDiff
from functools import reduce, wraps
from itertools import islice, groupby as itergroupby
from operator import itemgetter

import babel
import babel.dates
import markupsafe
import pytz
from lxml import etree, objectify

import odoo
import odoo.addons
# get_encodings, ustr and exception_to_unicode were originally from tools.misc.
# There are moved to loglevels until we refactor tools.
from odoo.loglevels import exception_to_unicode, get_encodings, ustr  # noqa: F401
import odoo.tools.misc 
from .config import config
from .float_utils import float_round
from .which import which
from persiantools.jdatetime import JalaiDate,JalaliDateTime
K = typing.TypeVar('K')
T = typing.TypeVar('T')
if typing.TYPE_CHECKING:
    from collections.abc import Callable, Collection, Sequence
    from odoo.api import Environment
    from odoo.addons.base.models.res_lang import LangData

    P = typing.TypeVar('P')



DATE_LENGTH = len(datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))



LDML_TO_STRFTIME = {
    "yyyy": "%Y",     # 4-digit year
    "yy": "%y",       # 2-digit year
    "MMMM": "%B",     # Full month name
    "MMM": "%b",      # Abbreviated month name
    "MM": "%m",       # 2-digit month
    "M": "%-m",       # Month without leading zero (Unix only)
    "dd": "%d",       # 2-digit day of month
    "d": "%-d",       # Day without leading zero (Unix only)
    "EEEE": "%A",     # Full weekday name
    "EEE": "%a",      # Abbreviated weekday name
    "E": "%a",        # Abbreviated weekday name (same as above)
    "e": "%w",        # Day of week (0=Sunday)
    "HH": "%H",       # 24-hour (zero-padded)
    "H": "%-H",       # 24-hour without padding (Unix only)
    "hh": "%I",       # 12-hour (zero-padded)
    "h": "%-I",       # 12-hour without padding (Unix only)
    "mm": "%M",       # Minutes
    "ss": "%S",       # Seconds
    "a": "%p",        # AM/PM
    "Z": "%z",        # UTC offset (+0000)
    "z": "%Z",        # Timezone name
    "SSS": ".%f",     # Microseconds (you must trim to 3 digits manually for milliseconds)
    "'T'": "T",       # Literal "T"
}


def convert_ldml_to_strftime(ldml_format):
    for ldml, strf in LDML_TO_STRFTIME.items():
        ldml_format = ldml_format.replace(ldml, strf)
    return ldml_format

def format_date(
    env: Environment,
    value: datetime.datetime | datetime.date | str,
    lang_code: str | None = None,
    date_format: str | typing.Literal[False] = False,
) -> str:
    """
        Formats the date in a given format.

        :param env: an environment.
        :param date, datetime or string value: the date to format.
        :param string lang_code: the lang code, if not specified it is extracted from the
            environment context.
        :param string date_format: the format or the date (LDML format), if not specified the
            default format of the lang.
        :return: date formatted in the specified format.
        :rtype: string
    """
    if not value:
        return ''
    if isinstance(value, str):
        if len(value) < DATE_LENGTH:
            return ''
        if len(value) > DATE_LENGTH:
            # a datetime, convert to correct timezone
            value = odoo.fields.Datetime.from_string(value)
            value = odoo.fields.Datetime.context_timestamp(env['res.lang'], value)
        else:
            value = odoo.fields.Datetime.from_string(value)
    elif isinstance(value, datetime.datetime) and not value.tzinfo:
        # a datetime, convert to correct timezone
        value = odoo.fields.Datetime.context_timestamp(env['res.lang'], value)

    lang = misc.get_lang(env, lang_code)
    if lang=="fa_IR":
        return JalaiDate(value).strftime(date_format,locale="fa")
    
        
    locale = babel_locale_parse(lang.code)
    if not date_format:
        date_format = posix_to_ldml(lang.date_format, locale=locale)

    assert isinstance(value, datetime.date)  # datetime is a subclass of date
    return babel.dates.format_date(value, format=date_format, locale=locale)


def format_datetime(
    env: Environment,
    value: datetime.datetime | str,
    tz: str | typing.Literal[False] = False,
    dt_format: str = 'medium',
    lang_code: str | None = None,
) -> str:
    """ Formats the datetime in a given format.

    :param env:
    :param str|datetime value: naive datetime to format either in string or in datetime
    :param str tz: name of the timezone  in which the given datetime should be localized
    :param str dt_format: one of “full”, “long”, “medium”, or “short”, or a custom date/time pattern compatible with `babel` lib
    :param str lang_code: ISO code of the language to use to render the given datetime
    :rtype: str
    """
    if not value:
        return ''
    if isinstance(value, str):
        timestamp = odoo.fields.Datetime.from_string(value)
    else:
        timestamp = value

    tz_name = tz or env.user.tz or 'UTC'
    utc_datetime = pytz.utc.localize(timestamp, is_dst=False)
    try:
        context_tz = pytz.timezone(tz_name)
        localized_datetime = utc_datetime.astimezone(context_tz)
    except Exception:
        localized_datetime = utc_datetime

    lang = get_lang(env, lang_code)

    locale = babel_locale_parse(lang.code or lang_code)  # lang can be inactive, so `lang`is empty
    if not dt_format:
        date_format = posix_to_ldml(lang.date_format, locale=locale)
        time_format = posix_to_ldml(lang.time_format, locale=locale)
        dt_format = '%s %s' % (date_format, time_format)

    # Babel allows to format datetime in a specific language without change locale
    # So month 1 = January in English, and janvier in French
    # Be aware that the default value for format is 'medium', instead of 'short'
    #     medium:  Jan 5, 2016, 10:20:31 PM |   5 janv. 2016 22:20:31
    #     short:   1/5/16, 10:20 PM         |   5/01/16 22:20
    # Formatting available here : http://babel.pocoo.org/en/latest/dates.html#date-fields
    return babel.dates.format_datetime(localized_datetime, dt_format, locale=locale)
    
    
    
if __name__=="__main__":
    ldml = "yyyy-MM-dd'T'HH:mm:ss"
    print(convert_ldml_to_strftime(ldml))