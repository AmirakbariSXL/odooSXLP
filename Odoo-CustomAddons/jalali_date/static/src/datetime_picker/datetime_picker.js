/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { localization } from "@web/core/l10n/localization";
import { user } from "@web/core/user";
import { isInRange, today } from "@web/core/l10n/dates";
import { 
  jDate,
  jStartOfYear,
  jgetStartOfDecade,
  jgetStartOfCentury,
  jStartOfEachMonth,
  jStartOfMonth,
  jEndOfMonth,
  jStartOf,
  jStartOfEeach,
  toPersianDigits
} from  "@jalali_date/jutils";
const { DateTime, Info } = luxon;

import { _t } from "@web/core/l10n/translation";
import { jEndOfYear, jToLuxonDate, jWeeksInMonth } from "../jutils";


const getStartOfWeek = (date) => {
  const { weekStart } = localization;
  return date.set({
    weekday: date.weekday < weekStart ? weekStart - 7 : weekStart,
  });
};


const numberRange = (min, max) => [...Array(max - min)].map((_, i) => i + min);


const jtoDateItem = ({
  isOutOfRange = false,
  isValid = true,
  label,
  range,
  extraClass,
  jlable,
}) => ({
  id: range[0].toISODate(),
  includesToday: isInRange(today(), range),
  isOutOfRange,
  isValid,
  label: jlable,
  range,
  extraClass,
});

function jtoWeekItem(weekDayItems) {
  const date = weekDayItems[3].range[0];
  const jday = jDate(date, "persian");
  return {
    number: jday.format("w"),
    days: weekDayItems,
  };
}

// Time constants

const MINUTES = numberRange(0, 60).map((minute) => [
  minute,
  String(minute || 0).padStart(2, "0"),
]);


const PRECISION_LEVELS = new Map()
  .set("days", {
    mainTitle: _t("Select month"),
    nextTitle: _t("Next month"),
    prevTitle: _t("Previous month"),
    step: { month: 1 },
    getTitle: (date, { additionalMonth }) => {
      if (!date) {
        date = DateTime.now();
      }
      const jday = jDate(date, "persian");
      const titles = [`${jday.format("MMMM")} ${jday.format("YYYY")}`];
      if (additionalMonth) {
        const jnext = jday.add("months", 1);
        titles.push(`${jnext.format("MMMM")} ${jnext.format("YYYY")}`);
      }
      return titles;
    },
    getItems: (
      date,
      {
        additionalMonth,
        maxDate,
        minDate,
        showWeekNumbers,
        isDateValid,
        dayCellClass,
      },
    ) => {
      if (!date) {
        date = DateTime.now();
      }
      const startDates = [date];
      if (additionalMonth) {
        startDates.push(date.plus({ month: 1 }));
      }
      return startDates.map((date, i) => {
        const startofmonth = jStartOfMonth(date);
        const endtofmonth = jEndOfMonth(date);

        const monthRange = [startofmonth, endtofmonth];
        /** @type {WeekItem[]} */
        const weeks = [];

        const weeks_in_month=jWeeksInMonth(startofmonth)
        let startOfNextWeek = getStartOfWeek(monthRange[0]);
        for (let w = 0; w < weeks_in_month.weekCount; w++) {
          const weekDayItems = [];
          // Generate all days of the week
          for (let d = 0; d < 7; d++) {
            const day = startOfNextWeek.plus({ day: d });
            const range = [day.startOf("day"), day.endOf("day")];
            const dayItem = jtoDateItem({
              isOutOfRange: !isInRange(day, monthRange),
              isValid:
                isInRange(range, [minDate, maxDate]) && isDateValid?.(day),
              label: "day",
              range,
              extraClass: dayCellClass?.(day) || "",
              jlable: String(day.toFormat("d",{numberingSystem: 'arabext'})),
            });
            weekDayItems.push(dayItem);
            if (d === 6) {
              startOfNextWeek = day.plus({ day: 1 });
            }
          }
          weeks.push(jtoWeekItem(weekDayItems));
        }
        // Generate days of week labels
        const daysOfWeek = weeks[0].days.map((d) => [
          d.range[0].weekdayShort,
          d.range[0].weekdayLong,
          Info.weekdays("narrow", { locale: d.range[0].locale })[
            d.range[0].weekday - 1
          ],
        ]);
        if (showWeekNumbers) {
          daysOfWeek.unshift(["#", _t("Week numbers"), "#"]);
        }
        return {
          id: `__month__${i}`,
          number: monthRange[0].month,
          daysOfWeek,
          weeks,
        };
      });
    },
  })
  .set("months", {
    mainTitle: _t("Select year"),
    nextTitle: _t("Next year"),
    prevTitle: _t("Previous year"),
    step: { year: 1 },
    getTitle: (date) => String(date.toFormat("y",{numberingSystem: 'arabext'})),
    getItems: (date, { maxDate, minDate }) => {
      const startOfYear = jStartOfYear(date);
      return numberRange(0, 12).map((i) => {
        const startOfMonth = jStartOfEachMonth(startOfYear, i);
        const range = [startOfMonth, jEndOfMonth(startOfMonth)];
        return jtoDateItem({
          isValid: isInRange(range, [minDate, maxDate]),
          label: "monthShort",
          range,
          jlable: startOfMonth.plus({ month: 1 })["monthShort"],
        });
      });
    },
  })
  .set("years", {
    mainTitle: _t("Select decade"),
    nextTitle: _t("Next decade"),
    prevTitle: _t("Previous decade"),
    step: { year: 10 },
    getTitle: (date) =>
      `${toPersianDigits(jgetStartOfDecade(date))} - ${toPersianDigits(jgetStartOfDecade(date) + 9)}`,
    getItems: (date, { maxDate, minDate }) => {
      const startOfDecade = jStartOf(date, "decade");
      return numberRange(GRID_MARGIN - 1, GRID_COUNT).map((i) => {
        let startOfYear = jStartOfEeach(startOfDecade, "year", i);
        if (startOfDecade.toFormat("M") == "12"){
          startOfYear=startOfYear.plus({day:1})
        }
        const jend_of_year =jEndOfYear(startOfYear)
        const range = [startOfYear,jend_of_year ];
        return jtoDateItem({
          isOutOfRange: i < 0 || i >= GRID_COUNT,
          isValid: isInRange(range, [minDate, maxDate]),
          label: "year",
          range,
          jlable: String(startOfYear.toFormat("y",{numberingSystem: 'arabext'})),
        });
      });
    },
  })
  .set("decades", {
    mainTitle: _t("Select century"),
    nextTitle: _t("Next century"),
    prevTitle: _t("Previous century"),
    step: { year: 100 },
    getTitle: (date) =>
      `${toPersianDigits(jgetStartOfCentury(date))} - ${toPersianDigits(jgetStartOfCentury(date) + 90)}`,
    getItems: (date, { maxDate, minDate }) => {
      const startOfCentury = jStartOf(date, "century");
      return numberRange(GRID_MARGIN - 1, GRID_COUNT).map((i) => {
        let startOfDecade = jToLuxonDate(jDate(startOfCentury,"persian").add("year", i * 10 ).toCalendar("gregorian"));
        if (startOfDecade.toFormat("M") == "12"){
          startOfDecade=startOfDecade.plus({day:1})
        }
        const range = [
          startOfDecade,
          jEndOfYear(jToLuxonDate(jDate(startOfDecade,"persian").add("year", 10 ).toCalendar("gregorian")))
        ];
        return jtoDateItem({
          label: "year",
          isOutOfRange: i < 0 || i >= GRID_COUNT,
          isValid: isInRange(range, [minDate, maxDate]),
          range,
          jlable: String(startOfDecade.toFormat("y",{numberingSystem: 'arabext'})),
        });
      });
    },
  });

// Other constants
const GRID_COUNT = 10;
const GRID_MARGIN = 1;

const isPersianUser = user.lang == "fa-IR";
if (isPersianUser) {
  patch(DateTimePicker.prototype, {
    get activePrecisionLevel() {
      return PRECISION_LEVELS.get(this.state.precision);
    },
    next(ev) {
      ev.preventDefault();
      const { step } = this.activePrecisionLevel;
      const [key, value] = Object.entries(step)[0];
      let date =jToLuxonDate(jDate(this.state.focusDate, "persian").add(key, value).toCalendar("gregorian"))
      if (date.toFormat("M") == "12"){
        date=date.plus({day:1})
      }
      this.state.focusDate = this.clamp(date);
    },
    previous(ev) {
      ev.preventDefault();
      const { step } = this.activePrecisionLevel;
      const [key, value] = Object.entries(step)[0];
      let date =jToLuxonDate(jDate(this.state.focusDate, "persian").subtract(key, value).toCalendar("gregorian"))
      if (date.toFormat("M") == "12"){
        date=date.plus({day:1})
      }
      this.state.focusDate = this.clamp(date);
    }
  })
}
