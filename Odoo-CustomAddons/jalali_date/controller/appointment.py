
import json

from babel.dates import format_datetime, format_date, format_time
from datetime import datetime
from urllib.parse import quote, unquote_plus
from werkzeug.exceptions import  NotFound


from odoo import  http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

from odoo.tools.misc import  get_lang

from odoo.addons.appointment.controllers.appointment  import AppointmentController
from persiantools.jdatetime import JalaliDate

import logging

_logger = logging.getLogger(__name__)


class AppointmentControllerPatch(AppointmentController):
    @http.route(['/appointment/<int:appointment_type_id>/info'],
                type='http', auth="public", website=True, sitemap=False)
    def appointment_type_id_form(self, appointment_type_id, date_time, duration, staff_user_id=None, resource_selected_id=None, available_resource_ids=None, asked_capacity=1, **kwargs):
        """
        Render the form to get information about the user for the appointment
    
        :param appointment_type_id: the appointment type id related
        :param date_time: the slot datetime selected for the appointment
        :param duration: the duration of the slot
        :param staff_user_id: the user selected for the appointment
        :param resource_selected_id: the resource selected for the appointment
        :param available_resource_ids: the resources info we want to propagate that are linked to the slot time
        :param asked_capacity: the asked capacity for the appointment
        :param filter_appointment_type_ids: see ``Appointment.appointments()`` route
        """
        _logger.error(f"inside appointment_type_id_form and datetime >>>>>>>>>>>>>>>>>>>>{date_time}")
        if not get_lang(request.env).code=="fa_IR":
            return super.appointment_type_id_form(self, appointment_type_id, date_time, duration, staff_user_id=None, resource_selected_id=None, available_resource_ids=None, asked_capacity=1, **kwargs)
        domain = self._appointments_base_domain(
            filter_appointment_type_ids=kwargs.get('filter_appointment_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )
        available_appointments = self._fetch_and_check_private_appointment_types(
            kwargs.get('filter_appointment_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        appointment_type = available_appointments.filtered(lambda appt: appt.id == int(appointment_type_id))
    
        if not appointment_type:
            raise NotFound()
    
        if not self._check_appointment_is_valid_slot(appointment_type, staff_user_id, resource_selected_id, available_resource_ids, date_time, duration, asked_capacity, **kwargs):
            raise NotFound()
    
        partner = self._get_customer_partner()
        partner_data = partner.read(fields=['name', 'phone', 'email'])[0] if partner else {}
        date_time = unquote_plus(date_time)
        date_time_object = datetime.strptime(date_time, dtf)
        day_name = format_datetime(date_time_object, 'EEE', locale=get_lang(request.env).code)
        # date_formated = format_date(date_time_object.date(), locale=get_lang(request.env).code)
        date_formated = JalaliDate(date_time_object.date()).strftime( '%d %B %Y',locale='fa')
        time_locale = format_time(date_time_object.time(), locale=get_lang(request.env).code, format='short')
        resource = request.env['appointment.resource'].sudo().browse(int(resource_selected_id)) if resource_selected_id else request.env['appointment.resource']
        staff_user = request.env['res.users'].browse(int(staff_user_id)) if staff_user_id else request.env['res.users']
        users_possible = self._get_possible_staff_users(
            appointment_type,
            json.loads(unquote_plus(kwargs.get('filter_staff_user_ids') or '[]')),
        )
        resources_possible = self._get_possible_resources(
            appointment_type,
            json.loads(unquote_plus(kwargs.get('filter_resource_ids') or '[]')),
        )
        return request.render("appointment.appointment_form", {
            'partner_data': partner_data,
            'appointment_type': appointment_type,
            'available_appointments': available_appointments,
            'main_object': appointment_type,
            'datetime': date_time,
            'date_locale': f'{day_name} {date_formated}',
            'time_locale': time_locale,
            'datetime_str': date_time,
            'duration_str': duration,
            'duration': float(duration),
            'staff_user': staff_user,
            'resource': resource,
            'asked_capacity': int(asked_capacity),
            'timezone': request.session.get('timezone') or appointment_type.appointment_tz,  # bw compatibility
            'users_possible': users_possible,
            'resources_possible': resources_possible,
            'available_resource_ids': available_resource_ids,
            'login_with_redirect_url': f'/web/login?redirect={quote(request.httprequest.full_path)}',
        })
    

    