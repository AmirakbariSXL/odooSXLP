import calendar as cal
from datetime import datetime, time
from dateutil import rrule
import pytz
from babel.dates import format_time
from dateutil.relativedelta import relativedelta
from persiantools.jdatetime import JalaliDate,JalaliDateTime
from werkzeug.urls import url_encode
from datetime import datetime, timedelta
import logging
from odoo import models,api,fields
from odoo.tools.misc import babel_locale_parse, get_lang
_logger = logging.getLogger(__name__)
from odoo.addons.jalali_date.py_utils.utils import jalali_month



class JalaliAppointmentType(models.Model):
    _inherit = "appointment.type"
    # jappointment_tz = fields.Datetime(compute='_compute_jappointment_tz', readonly=True,)
    # @api.depends('appointment_tz')
    # def _compute_jappointment_tz(self):
    #     for record in self:
    #         if record.appointment_tz:
    #             record.jappointment_tz = JalaliDateTime(record.appointment_tz)
    def _get_appointment_slots(
        self,
        timezone,
        filter_users=None,
        filter_resources=None,
        asked_capacity=1,
        reference_date=None,
    ):
        """
        :returns: list of dicts (1 per month) containing available slots per week
          and per day for each week (see ``_slots_generate()``), like
          [
            {'id': 0,
             'month': 'February 2022' (formatted month name),
             'weeks': [
                [{'day': '']
                [{...}],
             ],
            },
            {'id': 1,
             'month': 'March 2022' (formatted month name),
             'weeks': [ (...) ],
            },
            {...}
          ]
        """

        self.ensure_one()

        if not self.active:
            return []
        now = datetime.utcnow()
        if not reference_date:
            reference_date = now

        try:
            requested_tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            requested_tz = self.appointment_tz

        appointment_duration_days = self.max_schedule_days
        unique_slots = self.slot_ids.filtered(lambda slot: slot.slot_type == "unique")

        if self.category == "custom" and unique_slots:
            # Custom appointment type, the first day should depend on the first slot datetime
            start_first_slot = unique_slots[0].start_datetime
            first_day_utc = (
                start_first_slot
                if reference_date > start_first_slot
                else reference_date
            )
            first_day = requested_tz.fromutc(
                first_day_utc + relativedelta(hours=self.min_schedule_hours)
            )
            appointment_duration_days = (
                unique_slots[-1].end_datetime.date() - reference_date.date()
            ).days
            last_day = requested_tz.fromutc(
                reference_date + relativedelta(days=appointment_duration_days)
            )
        elif self.category == "punctual":
            # Punctual appointment type, the first day is the start_datetime if it is in the future, else the first day is now
            first_day = requested_tz.fromutc(
                self.start_datetime if self.start_datetime > now else now
            )
            last_day = requested_tz.fromutc(self.end_datetime)
        else:
            # Recurring appointment type
            first_day = requested_tz.fromutc(
                reference_date + relativedelta(hours=self.min_schedule_hours)
            )
            last_day = requested_tz.fromutc(
                reference_date + relativedelta(days=appointment_duration_days)
            )

        # Compute available slots (ordered)
        slots = self._slots_generate(
            first_day.astimezone(pytz.utc),
            # JalaliDateTime(first_day.astimezone(pytz.utc)),
            last_day.astimezone(pytz.utc),
            # JalaliDateTime(last_day.astimezone(pytz.utc)),
            timezone,
            reference_date=reference_date,
        )
        # _logger.error(f"Slots generated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>: {slots}")
        
        # No slots -> skip useless computation
        if not slots:
            return slots
        valid_users = (
            filter_users.filtered(lambda user: user in self.staff_user_ids)
            if filter_users
            else None
        )
        valid_resources = (
            filter_resources.filtered(lambda resource: resource in self.resource_ids)
            if filter_resources
            else None
        )
        # Not found staff user : incorrect configuration -> skip useless computation
        if filter_users and not valid_users:
            return []
        if filter_resources and not valid_resources:
            return []
        # Used to check availabilities for the whole last day as _slot_generate will return all slots on that date.
        last_day_end_of_day = datetime.combine(
            last_day.astimezone(pytz.timezone(self.appointment_tz)), time.max
        )
        if self.schedule_based_on == "users":
            self._slots_fill_users_availability(
                slots,
                first_day.astimezone(pytz.UTC),
                last_day_end_of_day.astimezone(pytz.UTC),
                valid_users,
            )
            slot_field_label = (
                "available_staff_users"
                if self.assign_method == "time_resource"
                else "staff_user_id"
            )
        else:
            self._slots_fill_resources_availability(
                slots,
                first_day.astimezone(pytz.UTC),
                last_day_end_of_day.astimezone(pytz.UTC),
                valid_resources,
                asked_capacity,
            )
            slot_field_label = "available_resource_ids"

        total_nb_slots = sum(slot_field_label in slot for slot in slots)
        # If there is no slot for the minimum capacity then we return an empty list.
        # This will lead to a screen informing the customer that there is no availability.
        # We don't want to return an empty list if the capacity as been tempered by the customer
        # as he should still be able to interact with the screen and select another capacity.
        if not total_nb_slots and asked_capacity == 1:
            return []
        nb_slots_previous_months = 0

        # Compute calendar rendering and inject available slots
        today = requested_tz.fromutc(reference_date)
        start = slots[0][timezone][0] if slots else today
        locale = babel_locale_parse(get_lang(self.env).code)
        month_dates_calendar = cal.Calendar(locale.first_week_day).monthdatescalendar
        months = []
        # glast_day = last_day
        # start = JalaliDateTime(start)
        # last_day = JalaliDateTime(last_day)
        # _logger.error(f"slots>>>>>>>>>>>>>>>>>>>>>>{slots}")
        # _logger.error(f"slots [0] >>>>>>>>>>>>>>>>>>>>>>{slots}")
        
        while (JalaliDateTime(start).year, JalaliDateTime(start).month) <= (JalaliDateTime(last_day).year, JalaliDateTime(last_day).month):
            nb_slots_next_months = sum(slot_field_label in slot for slot in slots)
            _logger.error(f"next months >>>>>>>>>>>>>>>>> {nb_slots_next_months}")
            has_availabilities = False
            # dates = month_dates_calendar(start.year, start.month)
            # dates = month_dates_calendar(JalaliDateTime(start).year, JalaliDateTime(start).month)
            dates = jalali_month(JalaliDateTime(start).year, JalaliDateTime(start).month)
            
            # jdates = jalali_month(start.year, start.month)
            _logger.error(f"jdates  >>>>>>>>>>>>>>>>>>>>> {dates}")
            for week_index, week in enumerate(dates):
                for day_index, day in enumerate(week):
                    mute_cls = weekend_cls = today_cls = None
                    today_slots = []
                    if day.weekday() in (locale.weekend_start, locale.weekend_end):
                        weekend_cls = "o_weekend bg-light"
                    if day == today.date() and day.month == today.month:
                        today_cls = "o_today"
                    if JalaliDate(day).month != JalaliDate(start).month:
                        mute_cls = "d-none"
                    else:
                        # slots are ordered, so check all unprocessed slots from until > day
                        
                        while slots and (slots[0][timezone][0].date() <= day):
                            if (slots[0][timezone][0].date() == day) and (
                                slot_field_label in slots[0]
                            ):
                                slot_start_dt_tz = JalaliDateTime(slots[0][timezone][0]).strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                                slot = {
                                    "datetime": slot_start_dt_tz,
                                    "available_resources": [
                                        {
                                            "id": resource.id,
                                            "name": resource.name,
                                            "capacity": resource.capacity,
                                        }
                                        for resource in slots[0][
                                            "available_resource_ids"
                                        ]
                                    ]
                                    if self.schedule_based_on == "resources"
                                    else False,
                                }
                                if (
                                    self.schedule_based_on == "users"
                                    and self.assign_method == "time_resource"
                                ):
                                    slot.update(
                                        {
                                            "available_staff_users": [
                                                {
                                                    "id": staff.id,
                                                    "name": staff.name,
                                                }
                                                for staff in slots[0][
                                                    "available_staff_users"
                                                ]
                                            ]
                                        }
                                    )
                                elif self.schedule_based_on == "users":
                                    slot.update(
                                        {"staff_user_id": slots[0]["staff_user_id"].id}
                                    )
                                if slots[0]["slot"].allday:
                                    slot_duration = 24
                                    slot.update(
                                        {
                                            "hours": _("All day"),
                                            "slot_duration": slot_duration,
                                        }
                                    )
                                else:
                                    start_hour = format_time(
                                        slots[0][timezone][0].time(),
                                        format="short",
                                        locale=locale,
                                    )
                                    end_hour = (
                                        format_time(
                                            slots[0][timezone][1].time(),
                                            format="short",
                                            locale=locale,
                                        )
                                        if self.category == "custom"
                                        else False
                                    )
                                    slot_duration = str(
                                        (
                                            slots[0][timezone][1]
                                            - slots[0][timezone][0]
                                        ).total_seconds()
                                        / 3600
                                    )
                                    slot.update(
                                        {
                                            "start_hour": start_hour,
                                            "end_hour": end_hour,
                                            "slot_duration": slot_duration,
                                        }
                                    )
                                url_parameters = {
                                    "date_time": slots[0][timezone][0].strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "duration": slot_duration,
                                }
                                if (
                                    self.schedule_based_on == "users"
                                    and self.assign_method != "time_resource"
                                ):
                                    url_parameters.update(
                                        staff_user_id=str(slots[0]["staff_user_id"].id)
                                    )
                                elif self.schedule_based_on == "resources":
                                    url_parameters.update(
                                        available_resource_ids=str(
                                            slots[0]["available_resource_ids"].ids
                                        )
                                    )
                                slot["url_parameters"] = url_encode(url_parameters)
                                today_slots.append(slot)
                                _logger.error(f"slot >>>>>>>>>>>>>>>>>>>>>>>> {slot}")
                                nb_slots_next_months -= 1
                            else:
                                _logger.error(f"inside else >>>>>>>>>>>>>>>>>{slots[0][timezone][0].date()}")
                            slots.pop(0)
                    today_slots = sorted(today_slots, key=lambda d: d["datetime"])
                    dates[week_index][day_index] = {
                        "day": JalaliDate(day),
                        "slots": today_slots,
                        "mute_cls": mute_cls,
                        "weekend_cls": weekend_cls,
                        "today_cls": today_cls,
                    }

                    has_availabilities = has_availabilities or bool(today_slots)

            months.append(
                {
                    "id": len(months),
                    # 'month': format_datetime(start, 'MMMM Y', locale=get_lang(self.env).code),
                    # "month": start.strftime("%B %Y"),
                    "month": JalaliDateTime(start).strftime("%B %Y",locale="fa"),
                    "weeks": dates,
                    "has_availabilities": has_availabilities,
                    "nb_slots_previous_months": nb_slots_previous_months,
                    "nb_slots_next_months": nb_slots_next_months,
                }
            )
            nb_slots_previous_months = total_nb_slots - nb_slots_next_months
            start = start + relativedelta(months=1)
            
        return months


