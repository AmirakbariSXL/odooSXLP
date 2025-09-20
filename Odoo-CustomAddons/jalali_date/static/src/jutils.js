const { DateTime } = luxon;

const MONTH_TO_START_OF_QUARTER ={
  1:1,
  2:1,
  3:1,
  4:4,
  5:4,
  6:4,
  7:7,
  8:7,
  9:7,
  10:10,
  11:10,
  12:10
}
const MONTH_TO_END_OF_QUARTER ={
  1:3,
  2:3,
  3:3,
  4:7,
  5:7,
  6:7,
  7:9,
  8:9,
  9:9,
  10:12,
  11:12,
  12:12,
}

const jToLuxonDate = (persiandate) => {
  return DateTime.fromObject({
    year: persiandate.year(),
    month: persiandate.month(),
    day: persiandate.day(),
  });
};
const jDate = (date=null, calendar = "gregorian", values = []) => {
  const date_parts =
    values.length == 3
      ? values
      : [+date.toFormat("y"), +date.toFormat("MM"), +date.toFormat("dd")];
  const jdate = new persianDate(date_parts).toCalendar(calendar);
  if (calendar == "persian") {
    return jdate;
  }
  return jToLuxonDate(jdate);
};

const jStartOfYear = (date) => {
  return jDate(undefined,undefined,[+date.toFormat("y"), 1, 1]);
}
const jEndOfYear = (date)=>{
  const jdate= jDate(date,"persian").endOf("year").toCalendar("gregorian");
  return jToLuxonDate(jdate)
}

const jStartOfMonth = (date) => {
  const jdate = jDate(date,"persian").startOf("month").toCalendar("gregorian");
  return jToLuxonDate(jdate)
};

const jEndOfMonth = (date) => {
  const jdate = jDate(date,"persian").endOf("month").toCalendar("gregorian");
  return jToLuxonDate(jdate)
};

const jStartOfQuarter = (date)=>{
  const jdate = jDate(undefined,"persian",[
    +date.toFormat("y"),
    MONTH_TO_START_OF_QUARTER[+date.toFormat("M")],
    1
  ]).toCalendar("gregorian");
  return jToLuxonDate(jdate)
}


const jEndOfQuarter = (date)=>{
  const jdate = jDate(undefined,"persian",[
    +date.toFormat("y"),
    MONTH_TO_END_OF_QUARTER[+date.toFormat("M")],
    1
  ]).endOf("month").toCalendar("gregorian");
  return jToLuxonDate(jdate)
}


const jgetStartOfDecade = (date) =>
  Math.floor(Math.round(+date.toFormat("y")) / 10) * 10;

const jgetStartOfCentury = (date) =>
  Math.floor(Math.round(+date.toFormat("y")) / 100) * 100;


const jStartOfEachMonth = (date, duration) => {
  const jdate = jDate(date,"persian").add("month", duration).startOf("month").toCalendar("gregorian");
  return jToLuxonDate(jdate)
};


const jStartOf = (date, unit) => {
  const divide = unit == "decade" ? 10 : 100;
  const startOfUnit =
    Math.floor(Math.round(+date.toFormat("y")) / divide) * divide;
  return jDate(undefined,undefined,[startOfUnit, 1, 1]);

};

const jStartOfEeach = (date, unit, duration) => {
  const jdate = jDate(date, "persian").add(unit, duration).startOf(unit).toCalendar("gregorian");
  return jToLuxonDate(jdate)
};
const jStartOfWeek = (date)=>{
  if (date.weekday == 6){
    return date
  }
  if (date.weekday == 7){
   date=date.plus({day:1})
  }
  return date.startOf("week").minus({day:2})
}

const jDayInMonth= (date)=>{
  return jDate(date,"persian").daysInMonth()
}

const jWeeksInMonth = (date)=>{
  const startofmonth =jStartOfMonth(date)
  const calnedar_start=jDate(jStartOfWeek(startofmonth),"persian") 
  const endtofmonth =jDate (jEndOfMonth(date),"persian")
  const calnedar_end=endtofmonth.endOf("week")
  const total_days=calnedar_end.diff(calnedar_start, "day") +1
  
  return {
    weekCount:Math.ceil(total_days / 7),
    startWeek:jToLuxonDate(calnedar_start.toCalendar("gregorian")),
    endWeek:jToLuxonDate(calnedar_end.toCalendar("gregorian"))
  }
}

const toPersianDigits = (str) => {
  return str.toString().replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d]);
}

const JalaliStartOf =(date,granularity) =>{
  if (granularity == "year"){
    return jStartOfYear(date)
  }
  else if(granularity == "month"){
    return jStartOfMonth(date)
  }
  else if(granularity == "quarter"){
    return jStartOfQuarter(date)
  }
}


const JalaliEndOf =(date,granularity) =>{
  if (granularity == "year"){
    return jEndOfYear(date)
  }
  else if(granularity == "month"){
    return jEndOfMonth(date)
  }
  else if(granularity == "quarter"){
    return jEndOfQuarter(date)
  }
}
export {
  jToLuxonDate,
  jDate,
  jStartOfYear,
  jEndOfYear,
  jgetStartOfDecade,
  jgetStartOfCentury,
  jStartOfEachMonth,
  jStartOfMonth,
  jEndOfMonth,
  jStartOf,
  jStartOfEeach,
  jWeeksInMonth,
  toPersianDigits,
  JalaliStartOf,
  JalaliEndOf
}
window.jDate=jDate
window.jStartOfMonth=jStartOfMonth
window.jEndOfMonth=jEndOfMonth
window.jStartOfYear=jStartOfYear
window.jStartOfWeek=jStartOfWeek
window.jDayInMonth=jDayInMonth
window.jWeeksInMonth=jWeeksInMonth
window.jToLuxonDate=jToLuxonDate
window.JalaliStartOf=JalaliStartOf
window.JalaliEndOf=JalaliEndOf