import { CalendarController } from "@web/views/calendar/calendar_controller";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { jDate } from "@jalali_date/jutils";

const isPersianUser = user.lang == "fa-IR";
if (isPersianUser) {
  patch(CalendarController.prototype, {
   
    get currentYear() {
        return this.date.toFormat("y");
    },

    get dayHeader() {
        return `${this.date.toFormat("dd")} ${this.date.toFormat("MMMM")} ${this.date.toFormat("y")}`;
    },

    get currentMonth() {
        return `${this.date.toFormat("MMMM")} ${this.date.toFormat("y")}`;
    },

    get currentWeek() {
        // return getLocalWeekNumber(this.model.rangeStart);
        return jDate(this.model.rangeStart,"persian").format("w")
    },

    get weekHeader() {
            const { rangeStart, rangeEnd } = this.model;
            const jrangeStart = jDate(rangeStart, "persian");
            const jrangeEnd =jDate(rangeEnd, "persian"); 
            if (jrangeStart.year() != jrangeEnd.year()) {
                return `${jrangeStart.format("MMMM")} ${jrangeStart.format("YYYY")} - ${jrangeEnd.format(
                    "MMMM"
                )} ${jrangeEnd.format("YYYY")}`;
            } else if (jrangeStart.month() != jrangeEnd.month()) {
                return `${jrangeStart.format("MMMM")} - ${jrangeEnd.format("MMMM")} ${
                jrangeStart.format("YYYY")
                }`;
            }
            return `${jrangeStart.format("MMMM")} ${jrangeStart.format("YYYY")}`;
        }

  })
}
  