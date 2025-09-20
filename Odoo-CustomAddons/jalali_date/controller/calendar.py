


import pytz

from babel.dates import format_datetime, format_date
from werkzeug.urls import url_encode
import datetime
from odoo import fields, _
from odoo.addons.appointment.controllers.calendar import AppointmentCalendarController
from odoo.http import request, route
from odoo.tools.misc import get_lang
from persiantools.jdatetime import JalaliDate,JalaliDateTime


class PatchAppointmentCalendarController(AppointmentCalendarController):
    @route(['/calendar/view/<string:access_token>'], type='http', auth="public", website=True)
    def appointment_view(self, access_token, partner_id=False, state=False, **kwargs):
        """
        Render the validation of an appointment and display a summary of it
    
        :param access_token: the access_token of the event linked to the appointment
        :param partner_id: id of the partner who booked the appointment
        :param state: allow to display an info message, possible values:
            - 'new': Info message displayed when the appointment has been correctly created
            - other values: see _get_prevent_cancel_status
        """
        locale = get_lang(request.env).code
        if not locale=="fa_IR":
            return super.appointment_view(self, access_token, partner_id=False, state=False, **kwargs)
        partner_id = int(partner_id) if partner_id else False
        event = request.env['calendar.event'].with_context(active_test=False).sudo().search([('access_token', '=', access_token)], limit=1)
        if not event:
            return request.not_found()
        timezone = request.session.get('timezone')
        if not timezone:
            timezone = request.env.context.get('tz') or event.appointment_type_id.appointment_tz or event.partner_ids and event.partner_ids[0].tz or event.user_id.tz or 'UTC'
            request.session['timezone'] = timezone
        tz_session = pytz.timezone(timezone)
    
        date_start_suffix = ""
        format_func = format_datetime
        if not event.allday:
            url_date_start = fields.Datetime.from_string(event.start).strftime('%Y%m%dT%H%M%SZ')
            url_date_stop = fields.Datetime.from_string(event.stop).strftime('%Y%m%dT%H%M%SZ')
            date_start = fields.Datetime.from_string(event.start).replace(tzinfo=pytz.utc).astimezone(tz_session)
        else:
            url_date_start = url_date_stop = fields.Date.from_string(event.start_date).strftime('%Y%m%d')
            date_start = fields.Date.from_string(event.start_date)
            format_func = format_date
            date_start_suffix = _(', All Day')
    
        
        day_name = format_func(date_start, 'EEE', locale=locale)
        date_start_date= JalaliDate(date_start).strftime('%d %B %Y',locale='fa') if isinstance(date_start,datetime.datetime) else JalaliDateTime(date_start).strftime('%d %B %Y %H:%M:%S',locale='fa')
        date_start = f'{day_name} {date_start_date}{date_start_suffix}'
        params = {
            'action': 'TEMPLATE',
            'text': event._get_customer_summary(),
            'dates': f'{url_date_start}/{url_date_stop}',
            'details': event._get_customer_description(),
        }
        if event.location:
            params.update(location=event.location.replace('\n', ' '))
        encoded_params = url_encode(params)
        google_url = 'https://www.google.com/calendar/render?' + encoded_params
    
        return request.render("appointment.appointment_validated", {
            'cancel_responsible': event.user_id if event.user_id.active and event.user_id._is_internal() else False,
            'event': event,
            'datetime_start': date_start,
            'google_url': google_url,
            'state': state,
            'partner_id': partner_id,
            'attendee_status': event.attendee_ids.filtered(lambda a: a.partner_id.id == partner_id).state if partner_id else False,
            'is_cancelled': not event.active,
        }, headers={'Cache-Control': 'no-store'})
