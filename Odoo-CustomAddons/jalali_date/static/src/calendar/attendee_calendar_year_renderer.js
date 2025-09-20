/** @odoo-module **/

import { AttendeeCalendarYearRenderer } from "@calendar/views/attendee_calendar/year/attendee_calendar_year_renderer";

AttendeeCalendarYearRenderer.props = {
  ...AttendeeCalendarYearRenderer.props,
  openWorkLocationWizard: { type: Function, optional: true },
};
