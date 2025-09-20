import { CalendarYearRenderer } from "@web/views/calendar/calendar_year/calendar_year_renderer";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import {
  jStartOfYear,
  jStartOfEachMonth,
  jDate,
  jEndOfMonth,
  jWeeksInMonth,
} from "../jutils";

const { DateTime } = luxon;
const persianMonths = [
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
const getViewForMonth = (date) => {
  return {
    jalaliDayGridMonth: {
      type: "dayGrid",
      visibleRange: {
        start: date.toISODate(),
        end: jEndOfMonth(date).plus({ day: 1 }).toISODate(),
      },
      duration: { weeks: jWeeksInMonth(date).weekCount },
      showNonCurrentDates: false,
    },
  };
};
const getJDateWithMonth = (date, month_number) => {
  const jstartofyear = jStartOfYear(date);
  return jStartOfEachMonth(jstartofyear, month_number);
};
const isPersianUser = user.lang == "fa-IR";
if (isPersianUser) {
  patch(CalendarYearRenderer.prototype, {
    getOptionsForMonth(month) {
      const initDate = getJDateWithMonth(
        this.props.model.date,
        this.months.indexOf(month),
      );
      

      return {
        ...this.options,
        initialDate: initDate.toISO(),
        initialView: "jalaliDayGridMonth",
        views: getViewForMonth(initDate),

        dayCellContent: function (arg) {
          const currentMonth = this.months.indexOf(month) + 1;
          const cellMonth = +DateTime.fromJSDate(arg.date).toFormat("M");
          if (cellMonth === currentMonth) {
            return DateTime.fromJSDate(arg.date).toFormat("d");
          }
          return "";
          
        },

        titleFormat: function (arg) {
          // return `${persianMonths[this.months.indexOf(month)]} ${initDate.toFormat("y")}`;
          return persianMonths[this.months.indexOf(month)];
        },
      };
    },

    getDayCellClassNames(info) {
      const date = luxon.DateTime.fromJSDate(info.date);
      const currentMonth = persianMonths.indexOf(info.view.getCurrentData().viewTitle) + 1;
      const cellMonth = +date.toFormat("M");
      let classes = [];
      if (cellMonth !== currentMonth){
        classes.push("o_persian_disabled")
      }
      else {
        if (date.weekday==5) {
          classes.push("o_calendar_disabled")
        }
      }
      return classes
    },

    getDateWithMonth(month) {
      return this.props.model.date.set({
        month: this.months.indexOf(month) + 1,
      });
    },
  });
}
