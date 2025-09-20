# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    signature = fields.Binary(string='Signature', help='Attach the signature here')