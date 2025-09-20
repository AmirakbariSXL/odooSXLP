import {AccountReportFilters} from "@account_reports/components/account_report/filters/filters";
import {patch} from "@web/core/utils/patch";
patch(AccountReportFilters.prototype, {
  dateFrom(optionKey) {
    console.log("date from ",this.controller.options[optionKey].date_from)
      return DateTime.fromISO(this.controller.options[optionKey].date_from);
  },

  dateTo(optionKey) {
    console.log("date to ",this.controller.options[optionKey].date_to)
      return DateTime.fromISO(this.controller.options[optionKey].date_to);
  }
});