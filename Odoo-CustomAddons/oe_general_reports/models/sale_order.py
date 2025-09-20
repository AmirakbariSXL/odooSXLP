# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    subtotal_amount_per_line = fields.Monetary(compute='sale_order_compute')
    subtotal_discount = fields.Monetary(compute='sale_order_compute')
    total_discount = fields.Monetary(compute='sale_order_compute')
    amount_discounted = fields.Monetary(compute='sale_order_compute')
    total_taxes = fields.Monetary(compute='sale_order_compute')
    subtotal_amount_plus_tax_per_line = fields.Monetary(compute='sale_order_compute')
    def sale_order_compute(self):
        self.ensure_one()
        subtotal_amount_per_line = 0
        subtotal_discount = 0
        total_discount = 0
        amount_discounted = 0
        total_taxes = 0
        subtotal_amount_plus_tax_per_line = 0
        for line in self.order_line:
            subtotal_discount += (line.discount/100) * (line.price_unit)*(line.product_uom_qty)
            if self.company_id.sale_discount_product_id.id == line.product_id.id:
                total_discount += line.amount_plus_tax_per_line
            else:
                subtotal_amount_per_line += line.amount_per_line
                amount_discounted += line.price_subtotal
                total_taxes += line.price_tax
                subtotal_amount_plus_tax_per_line += line.amount_plus_tax_per_line
        self.subtotal_amount_per_line= subtotal_amount_per_line
        self.subtotal_discount = subtotal_discount
        self.total_discount = abs(total_discount)
        self.amount_discounted = amount_discounted
        self.total_taxes = total_taxes
        self.subtotal_amount_plus_tax_per_line = subtotal_amount_plus_tax_per_line
