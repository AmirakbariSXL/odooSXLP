# -*- coding: utf-8 -*-

from odoo import fields, models, _
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amount_per_line = fields.Monetary(compute='sale_order_line_compute')
    discount_per_line = fields.Monetary(compute='sale_order_line_compute')
    amount_plus_tax_per_line = fields.Monetary(compute='sale_order_line_compute')

    def sale_order_line_compute(self):
        for line in self:
            line.amount_per_line = line.product_uom_qty*line.price_unit
            line.discount_per_line = line.discount / 100 * line.price_unit * line.product_uom_qty 
            line.amount_plus_tax_per_line = line.price_subtotal + line.price_tax

