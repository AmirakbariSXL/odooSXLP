
from persiantools.jdatetime import JalaliDateTime,JalaliDate
import datetime

def date_type(date):
    return "date" if isinstance(date, datetime.date) else "datetime"

def j_start_of(date,unit):
    if not (isinstance(date, datetime.date) or isinstance(date, datetime.datetime)):
        raise TypeError("date must be a datetime.date object and unit must be a string")
    calc_point = "start"
    type=date_type(date)
    if unit == 'year':
        return year(date,calc_point,type)
    elif unit == 'month':
        return month(date,calc_point,type)
    else:
        raise ValueError("unit must be 'year', 'month'")


def j_end_of(date,unit):
    if not (isinstance(date, datetime.date) or isinstance(date, datetime.datetime)):
        raise TypeError("date must be a datetime.date object")
    calc_point = "end"
    type=date_type(date)
    if unit == 'year':
        return year(date,calc_point,type)
    elif unit == 'month':
        return month(date,calc_point,type)
    else:
        raise ValueError("unit must be 'year', 'month'")

def jweek_info(date):
    if not (isinstance(date,( datetime.date,datetime.datetime,JalaliDate,JalaliDateTime))):
        raise TypeError("date must be a datetime.date object")
    if not isinstance(date, (JalaliDate,JalaliDateTime)):
        jdate=JalaliDate(date) if isinstance(date, datetime.date) else JalaliDateTime(date)
    else:
        jdate=date
    week_number=jdate.isocalendar()[1]-1
    start_of_week = jdate - datetime.timedelta(days=jdate.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    return {
        'week_number': week_number,
        'start_of_week': start_of_week.to_gregorian(),
        'end_of_week': end_of_week.to_gregorian()
    }

def year(date,calc_point,type="date"):
    jdate=JalaliDate(date) if type == "date" else JalaliDateTime(date)
    if calc_point == "start":
        return jdate.replace(month=1,day=1).to_gregorian()
    elif calc_point == "end":
        days_in_month=JalaliDate.days_in_month(12,jdate.year)
        return jdate.replace(month=12,day=days_in_month).to_gregorian()
        
def month(date,calc_point,type="date"):
    jdate=JalaliDate(date) if type == "date" else JalaliDateTime(date)
    if calc_point == "start":
        return jdate.replace(day=1).to_gregorian()
    elif calc_point == "end":
        days_in_month=JalaliDate.days_in_month(jdate.month,jdate.year)
        return jdate.replace(day=days_in_month).to_gregorian()
    
    
def weeks_in_month(year,month):
    date=JalaliDate(year,month,1).to_gregorian()
    start_of_month = j_start_of(date, "month")
    end_of_month = j_end_of(date, "month")
    start_of_week_in_month = jweek_info(start_of_month)["start_of_week"]
    end_of_week_in_month = jweek_info(end_of_month)["end_of_week"]
    total_days = (end_of_week_in_month - start_of_week_in_month)
   
    return {
        'weeks': int((total_days.days+1) / 7),
        'start': start_of_week_in_month,
        'end': end_of_week_in_month
    }


def jalali_month(year, month):
    week_range=weeks_in_month(year, month)
    week_days=[]
    jmonth=[]
    days=0
    for week in range(1,week_range["weeks"]+1):
        for weekday in range (1,8):
            week_days.append(week_range["start"] + datetime.timedelta(days=days))
            days+=1
        jmonth.append(week_days)
        week_days=[]
    return jmonth

if __name__ == "__main__":
    date = datetime.date(2025, 7, 8)
    # print(jweek_info(date))
    # print(weeks_in_month(date))
    # print(j_start_of(date, "year"))
    # print(j_start_of(date, "month"))
    from pprint import pprint
    
    pprint(jalali_month(2025,7))
    