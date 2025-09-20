# -*- coding: utf-8 -*-

from odoo import fields, models
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    amount_per_line = fields.Monetary(compute='account_move_line_compute')
    discount_per_line = fields.Monetary(compute='account_move_line_compute')
    price_tax = fields.Monetary(compute='account_move_line_compute')

    def account_move_line_compute(self):
        for line in self:
            line.amount_per_line = line.quantity*line.price_unit
            line.discount_per_line = line.discount / 100 * line.price_unit * line.quantity 
            line.price_tax = line.price_total - line.price_subtotal
