

import logging
from odoo.tools import ( date_utils,
    DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT,
    get_lang,)
from odoo import models,api
import datetime
import pytz
import babel.dates
from persiantools.jdatetime import JalaliDateTime,JalaliDate
_logger = logging.getLogger(__name__)



READ_GROUP_NUMBER_GRANULARITY = {
    "year_number": "year",
    "quarter_number": "quarter",
    "month_number": "month",
    "iso_week_number": "week",  # ISO week number because anything else than ISO is nonsense
    "day_of_year": "doy",
    "day_of_month": "day",
    "day_of_week": "dow",
    "hour_number": "hour",
    "minute_number": "minute",
    "second_number": "second",
}
READ_GROUP_DISPLAY_FORMAT = {
    # Careful with week/year formats:
    #  - yyyy (lower) must always be used, *except* for week+year formats
    #  - YYYY (upper) must always be used for week+year format
    #         e.g. 2006-01-01 is W52 2005 in some locales (de_DE),
    #                         and W1 2006 for others
    #
    # Mixing both formats, e.g. 'MMM YYYY' would yield wrong results,
    # such as 2006-01-01 being formatted as "January 2005" in some locales.
    # Cfr: http://babel.pocoo.org/en/latest/dates.html#date-fields
    'hour': 'hh:00 dd MMM',
    'day': 'dd MMM yyyy', # yyyy = normal year
    'week': "'W'w YYYY",  # w YYYY = ISO week-year
    'month': 'MMMM yyyy',
    'quarter': 'QQQ yyyy',
    'year': 'yyyy',
}



JREAD_GROUP_DISPLAY_STRFTIME = {
    'hour': '%H:00 %d %b',
    'day': '%d %B %Y',
    'week': "هفته %W %Y",           # or "W%U %Y" depending on week numbering
    'month': '%B %Y',
    'quarter': 'Q%q %Y',        # no direct support, will explain below
    'year': '%Y',
}
jdate_type={
     "date":JalaliDate,
     "datetime":JalaliDateTime,
 }

def date_type(date):
    return jdate_type["date"] if type(date)=="datetime.date" else jdate_type["datetime"]
    
def turn_jrange_to_parts(range,granularity):
    if granularity == 'week':
        return range.start.isocalendar()[1], range.end.isocalendar()[1]
    elif granularity == 'month':
        return range.start.month, range.end.month
    elif granularity == 'quarter':
        return range.start.quarter, range.end.quarter
    elif granularity == 'year':
        return range.start.year, range.end.year
    else:
        raise ValueError(f"Invalid granularity: {granularity}")

def jsort(result_dict,granularity,group,dt_type):
    # _logger.error(f"dict in jsort >>>>>>>>>>>>>>>>>> {dict}")
    # _logger.error(f"granularity in jsort >>>>>>>>>>>>>>>>>> {granularity}")
    
    new_result =[]
    result_date_range={
        "start":dt_type(result_dict[0][group])if result_dict else None,
        "end":dt_type(result_dict[-1][group])if result_dict else None,
    }
    result_date_parts=turn_jrange_to_parts(result_date_range,granularity)
    for item in result_dict :
        
        item_date=dt_type(item[group])
    
    _logger.error(f"new_dict  in jsort >>>>>>>>>>>>>>>>>> {type(result_dict)}")
        
        
    






@api.model
def _read_group_format_result(self, rows_dict, lazy_groupby):
    """
        Helper method to format the data contained in the dictionary data by
        adding the domain corresponding to its values, the groupbys in the
        context and by properly formatting the date/datetime values.

    :param data: a single group
    :param annotated_groupbys: expanded grouping metainformation
    :param groupby: original grouping metainformation
    """
    for group in lazy_groupby:
        field_name = group.split(':')[0].split('.')[0]
        field = self._fields[field_name]

        if field.type in ('date', 'datetime'):
            granularity = group.split(':')[1] if ':' in group else 'month'
            if granularity in models.READ_GROUP_TIME_GRANULARITY:
                locale = get_lang(self.env).code
                fmt = DEFAULT_SERVER_DATETIME_FORMAT if field.type == 'datetime' else DEFAULT_SERVER_DATE_FORMAT
                interval = models.READ_GROUP_TIME_GRANULARITY[granularity]
        elif field.type == "properties":
            self._read_group_format_result_properties(rows_dict, group)
            continue

        for row in rows_dict:
            value = row[group]

            if isinstance(value, models.BaseModel):
                row[group] = (value.id, value.sudo().display_name) if value else False
                value = value.id

            if not value and field.type == 'many2many':
                other_values = [other_row[group][0] if isinstance(other_row[group], tuple)
                                else other_row[group].id if isinstance(other_row[group], models.BaseModel)
                                else other_row[group] for other_row in rows_dict if other_row[group]]
                additional_domain = [(field_name, 'not in', other_values)]
            else:
                additional_domain = [(field_name, '=', value)]

            if field.type in ('date', 'datetime'):
                if value and isinstance(value, (datetime.date, datetime.datetime)):
                    # jsort(rows_dict,granularity,group,date_type(value))
                    
                    _logger.error(f"rows_dict  in jsort >>>>>>>>>>>>>>>>>> {rows_dict}")
                    range_start = value
                    range_end = value + interval
                    if field.type == 'datetime':
                        tzinfo = None
                        if self._context.get('tz') in pytz.all_timezones_set:
                            tzinfo = pytz.timezone(self._context['tz'])
                            range_start = tzinfo.localize(range_start).astimezone(pytz.utc)
                            # take into account possible hour change between start and end
                            range_end = tzinfo.localize(range_end).astimezone(pytz.utc)
                        if locale == "fa_IR":
                            label = JalaliDateTime(range_start,tzinfo=tzinfo).strftime(JREAD_GROUP_DISPLAY_STRFTIME[granularity],locale="fa")
                        else:
                            label = babel.dates.format_datetime(
                                range_start, format=READ_GROUP_DISPLAY_FORMAT[granularity],
                                tzinfo=tzinfo, locale=locale
                            )
                    else:
                        if locale=="fa_IR":
                            label = JalaliDate(value).strftime(JREAD_GROUP_DISPLAY_STRFTIME[granularity],locale="fa")
                        else:
                            label = babel.dates.format_date(
                                value, format=READ_GROUP_DISPLAY_FORMAT[granularity],
                                locale=locale
                            )
                    # special case weeks because babel is broken *and*
                    # ubuntu reverted a change so it's also inconsistent
                    if granularity == 'week':
                        if locale=="fa_IR":
                            iso_year, iso_week, iso_weekday = JalaliDate(value).isocalendar()
                            year, week , _= JalaliDate(value).isocalendar()
                            label = f"هفته {week} سال {year}"
                        else:
                            year, week = date_utils.weeknumber(
                                babel.Locale.parse(locale),
                                value,  # provide date or datetime without UTC conversion
                            )
                            label = f"W{week} {year:04}"

                    range_start = range_start.strftime(fmt)
                    range_end = range_end.strftime(fmt)
                    row[group] = label  # TODO should put raw data
                    row.setdefault('__range', {})[group] = {'from': range_start, 'to': range_end}
                    additional_domain = [
                        '&',
                            (field_name, '>=', range_start),
                            (field_name, '<', range_end),
                    ]
                elif value is not None and granularity in READ_GROUP_NUMBER_GRANULARITY:
                    additional_domain = [(f"{field_name}.{granularity}", '=', value)]
                elif not value:
                    # Set the __range of the group containing records with an unset
                    # date/datetime field value to False.
                    row.setdefault('__range', {})[group] = False

            row['__domain'] = expression.AND([row['__domain'], additional_domain])



@api.model
def _read_group_get_annotated_groupby(self, groupby, lazy):
    groupby = [groupby] if isinstance(groupby, str) else groupby
    lazy_groupby = groupby[:1] if lazy else groupby

    annotated_groupby = {}  # Key as the name in the result, value as the explicit groupby specification
    for group_spec in lazy_groupby:
        field_name, property_name, granularity = models.parse_read_group_spec(group_spec)
        if field_name not in self._fields:
            raise ValueError(f"Invalid field {field_name!r} on model {self._name!r}")
        field = self._fields[field_name]
        if property_name and field.type != 'properties':
            raise ValueError(f"Property name {property_name!r} has to be used on a property field.")
        if field.type in ('date', 'datetime'):
            # annotated_groupby[group_spec] = f"{field_name}:{granularity or 'month'}"
            annotated_groupby[group_spec] = f"{field_name}:{'day'}"
        else:
            annotated_groupby[group_spec] = group_spec
    return annotated_groupby


models.BaseModel._read_group_format_result = _read_group_format_result
models.BaseModel._read_group_get_annotated_groupby = _read_group_get_annotated_groupby

from odoo.osv import expression
