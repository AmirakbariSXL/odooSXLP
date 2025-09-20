# -*- coding: utf-8 -*-

from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"
    subtotal_amount_per_line = fields.Monetary(compute='account_move_compute')
    subtotal_discount = fields.Monetary(compute='account_move_compute')
    total_discount = fields.Monetary(compute='account_move_compute')
    amount_discounted = fields.Monetary(compute='account_move_compute')
    amount_undiscounted = fields.Monetary(compute='account_move_compute')
    total_taxes = fields.Monetary(compute='account_move_compute')
    subtotal_amount_plus_tax_per_line = fields.Monetary(compute='account_move_compute')

    def account_move_compute(self):
        self.ensure_one()
        subtotal_amount_per_line = 0
        subtotal_discount = 0
        total_discount = 0
        amount_discounted = 0
        amount_undiscounted = 0
        total_taxes = 0
        
        for invoice_line_id in self.invoice_line_ids:
            subtotal_discount += (invoice_line_id.discount/100) * (invoice_line_id.price_unit)*(invoice_line_id.quantity)
            amount_undiscounted += (invoice_line_id.price_subtotal * 100)/(100-invoice_line_id.discount) if invoice_line_id.discount != 100 else (invoice_line_id.price_unit * invoice_line_id.product_uom_qty)
            if self.company_id.sale_discount_product_id.id == invoice_line_id.product_id.id:
                total_discount+=invoice_line_id.price_total
            else:
                subtotal_amount_per_line += invoice_line_id.amount_per_line
                amount_discounted += invoice_line_id.price_subtotal
                total_taxes += invoice_line_id.price_tax
                
        self.subtotal_amount_per_line= subtotal_amount_per_line                
        self.subtotal_discount = subtotal_discount
        self.total_discount = abs(total_discount)
        self.amount_discounted = amount_discounted        
        self.amount_undiscounted = amount_undiscounted
        self.total_taxes = total_taxes
