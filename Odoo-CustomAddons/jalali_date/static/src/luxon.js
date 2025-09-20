import { user } from "@web/core/user";

const isPersianUser = user.lang == "fa-IR";

if (isPersianUser) {
  luxon.Settings.defaultOutputCalendar = "persian";
  luxon.Settings.defaultLocale = "fa-IR";
}
