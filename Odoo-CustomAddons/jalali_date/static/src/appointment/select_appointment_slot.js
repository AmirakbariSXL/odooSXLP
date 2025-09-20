/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement} from "@web/core/utils/render";
import { jDate } from "../jutils";
const {DateTime} = luxon
publicWidget.registry.appointmentSlotSelect = publicWidget.registry.appointmentSlotSelect.extend({
    _renderNoAvailabilityForMonth: function (monthEl) {
      const firstAvailabilityDate = this.firstEl.getAttribute("id");
      console.log("first availability date :",firstAvailabilityDate)
      let jdate=firstAvailabilityDate.split("-")
      console.log("jdate:",jdate)
      jdate=jDate(undefined,undefined,[+jdate[0],+jdate[1],+jdate[2]])
      console.log("jdate date :",jdate)
      console.log("jdate date :",jdate.toFormat("cccc dd MMMM yyyy"))
      const staffUserEl = this.el.querySelector("#slots_form select[name='staff_user_id']");
      const staffUserNameSelectedOption = staffUserEl?.options[staffUserEl.selectedIndex];
      const staffUserName = staffUserNameSelectedOption?.textContent;
      monthEl.querySelectorAll("table").forEach((tableEl) => tableEl.classList.add("d-none"));
      monthEl.append(
          renderToElement("Appointment.appointment_info_no_slot_month", {
            firstAvailabilityDate: jdate.reconfigure({ outputCalendar: "persian" }).toFormat("cccc dd MMMM yyyy"),
              staffUserName: staffUserName,
          })
      );
      monthEl
          .querySelector("#next_available_slot")
          .addEventListener("click", () => this.selectFirstAvailableMonth());
    }
});
