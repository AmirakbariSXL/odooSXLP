from odoo import api, fields
from odoo.addons.base.models.ir_qweb_fields import DateConverter, DateTimeConverter
from persiantools.jdatetime import JalaliDate


class JalaliDateConverter(DateConverter):
    _inherit = "ir.qweb.field.date"

    @api.model
    def value_to_html(self, value, options):
        lang = self.user_lang()
        if lang.code.startswith("fa") and value:
            try:
                if isinstance(value, str):
                    value = fields.Date.from_string(value)
                return JalaliDate(value).strftime("%Y/%m/%d")
            except Exception:
                pass
        return super().value_to_html(value, options)


class JalaliDateTimeConverter(DateTimeConverter):
    _inherit = "ir.qweb.field.datetime"

    @api.model
    def value_to_html(self, value, options):
        lang = self.user_lang()
        if lang.code.startswith("fa") and value:
            try:
                if isinstance(value, str):
                    value = fields.Datetime.from_string(value)
                j_date = JalaliDate(value.date()).strftime("%Y/%m/%d")
                j_time = value.strftime("%H:%M")
                return f"{j_date} {j_time}"
            except Exception:
                pass
        return super().value_to_html(value, options)
