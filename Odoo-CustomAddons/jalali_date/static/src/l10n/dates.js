/** @odoo-module **/
import * as DateUtils from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";
import { user } from "@web/core/user";
const { Settings, DateTime } = luxon;
const dateTimeCache = new WeakMap();
const dateCache = new WeakMap();

const SERVER_DATE_FORMAT = "yyyy-MM-dd";
const SERVER_TIME_FORMAT = "HH:mm:ss";
const SERVER_DATETIME_FORMAT = `${SERVER_DATE_FORMAT} ${SERVER_TIME_FORMAT}`;

const isPersianUser = user.lang == "fa-IR";
if (isPersianUser) {
  function serializeDate(value) {
    if (!dateCache.has(value)) {
      dateCache.set(
        value,
        value
          .reconfigure({ outputCalendar: "gregory" })
          .toFormat(SERVER_DATE_FORMAT, { numberingSystem: "latn" }),
      );
    }
    return dateCache.get(value);
  }
  function serializeDateTime(value) {
    if (!dateTimeCache.has(value)) {
      dateTimeCache.set(
        value,
        value
          .reconfigure({ outputCalendar: "gregory" })
          .setZone("utc")
          .toFormat(SERVER_DATETIME_FORMAT, { numberingSystem: "latn" }),
      );
    }
    return dateTimeCache.get(value);
  }
  function getLocalWeekNumber(date) {
    const jdate = jDate(DateTime.fromJSDate(date), "persian");
    jdate.formatPersian = false;
    return +jdate.format("w");
    // return getLocalYearAndWeek(date).week;
  }
  
 
  function formatDate(value, options = {}) {
      if (!value) {
          return "";
      }
      let format = options.format;
      if (!format) {
          format = localization.dateFormat;
          if (options.condensed) {
              format = getCondensedFormat(format);
          }
      }
      console.log("format",format)
      return value.toFormat(format);
  }
  
  function formatDateTime(value, options = {}) {
      if (!value) {
          return "";
      }
      let format = options.format;
      if (!format) {
          if (options.showSeconds === false) {
              format = `${localization.dateFormat} ${localization.shortTimeFormat}`;
          } else {
              format = localization.dateTimeFormat;
          }
          if (options.condensed) {
              format = getCondensedFormat(format);
          }
      }
      console.log("format",format)
      return value.setZone(options.tz || "default").toFormat(format);
  }
  DateUtils.MIN_VALID_DATE = DateTime.fromObject({ year: 1000 });
  DateUtils.MAX_VALID_DATE = DateTime.fromObject({ year: 3770 }).endOf("year");
  DateUtils.formatDateTime = formatDateTime;
  DateUtils.formatDate = formatDate;
  DateUtils.getLocalWeekNumber = getLocalWeekNumber;
  DateUtils.serializeDate = serializeDate;
  DateUtils.serializeDateTime = serializeDateTime;
}
