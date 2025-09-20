# -*- coding: utf-8 -*-
from odoo import fields, models

class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    signature = fields.Binary(string='Signature', related='company_id.signature', help='Attach the signature here')
