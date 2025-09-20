import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { getLocalWeekNumber, is24HourFormat } from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";
import { jDate, jEndOfMonth, jStartOfMonth, jWeeksInMonth } from "../jutils";
const { DateTime } = luxon;
const isPersianUser = user.lang == "fa-IR";

const getViewFor = (date) => {
  const new_date=jWeeksInMonth(date)
  return {
    jalaliDayGridMonth: {
      type: "dayGrid",
      visibleRange: {
        // start: jStartOfMonth(date).toISODate(),
        // end: jEndOfMonth(date).plus({day:1}).toISODate(),
        start: new_date.startWeek.toISODate(),
        end: new_date.endWeek.toISODate(),
      },
      duration:{weeks:new_date.weekCount}
    },
  }
}

const SCALE_TO_FC_VIEW = {
  day: "timeGridDay",
  week: "timeGridWeek",
  month: "jalaliDayGridMonth",
};
const SCALE_TO_HEADER_FORMAT = {
  day: "DDD",
  week: "EEE d",
  month: "EEEE",
};
const PERSIAN_MONTHS = [
  "فروردین",
  "اردیبهشت",
  "خرداد",
  "تیر",
  "مرداد",
  "شهریور",
  "مهر",
  "آبان",
  "آذر",
  "دی",
  "بهمن",
  "اسفند",
];
const originalOptionsGetter = Object.getOwnPropertyDescriptor(
  CalendarCommonRenderer.prototype,
  "options",
).get;

if (isPersianUser) {
  patch(CalendarCommonRenderer.prototype, {
    get options() {
      const default_options = originalOptionsGetter.call(this);
      const initDate = this.props.model.date;
      
      return {
        ...default_options,
        initialDate: this.props.model.scale === "month" ? jStartOfMonth(initDate).toISODate() : initDate.toISODate(),
        initialView: SCALE_TO_FC_VIEW[this.props.model.scale],
        views: getViewFor(initDate),
        dayCellContent: function (arg) {
          return DateTime.fromJSDate(arg.date).toFormat("d");
        },

      };
    },

    headerTemplateProps(date) {
      const scale = this.props.model.scale;
      const options = scale === "month" ? { zone: "UTC" } : {};
      const jdate = DateTime.fromJSDate(date, options);
      const { weekdayShort, weekdayLong } = jdate;
      const day = jdate.toFormat("dd");
      return {
        weekdayShort,
        weekdayLong,
        day,
        scale,
      };
    },
    getDayCellClassNames(info) {
      const date = luxon.DateTime.fromJSDate(info.date);
      const currentMonth = +DateTime.now().toFormat('M')
      const cellMonth = +date.toFormat("M");
      let classNames = [];
      if (cellMonth !== currentMonth){
        classNames.push("fc-day-other")
      }
      else {
        if (date.weekday==5) {
          classNames.push("o_calendar_disabled")
        }
      }
      return classNames
    },
  });
}
