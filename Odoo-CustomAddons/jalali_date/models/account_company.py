from odoo import models,fields
from odoo.addons.jalali_date.py_utils.utils import j_start_of

MONTH_SELECTION = [
    ('1', 'Farvardin'),
    ('2', 'Ordibehesht'),
    ('3', 'Khordad'),
    ('4', 'Tir'),
    ('5', 'Mordad'),
    ('6', 'Shahrivar'),
    ('7', 'Mehr'),
    ('8', 'Aban'),
    ('9', 'Azar'),
    ('10', 'Dey'),
    ('11', 'Bahman'),
    ('12', 'Esfand'),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    fiscalyear_last_month = fields.Selection(MONTH_SELECTION, default='12', required=True)
    account_opening_date = fields.Date(string='Opening Entry', default=lambda self: j_start_of(fields.Date.context_today(self), "year"), required=True, help="That is the date of the opening entry.")