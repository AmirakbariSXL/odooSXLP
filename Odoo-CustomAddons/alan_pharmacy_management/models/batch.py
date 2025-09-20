from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class AlanPharmaBatch(models.Model):
    _name = 'alan.pharma.batch'
    _description = 'Medicine Batch'
    _order = 'expiry_date'

    name = fields.Char(string='Batch Number', required=True)
    medicine_id = fields.Many2one('alan.pharma.medicine', string='Medicine', required=True, ondelete='cascade')
    quantity = fields.Float(string='Quantity', default=0.0)
    mfg_date = fields.Date(string='Mfg Date')
    expiry_date = fields.Date(string='Expiry Date')
    cost_price = fields.Float(string='Cost Price')
    selling_price = fields.Float(string='Selling Price')
    lot_barcode = fields.Char(string='Batch Barcode')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.constrains('expiry_date', 'mfg_date')
    def _check_dates(self):
        for rec in self:
            if rec.mfg_date and rec.expiry_date and rec.expiry_date <= rec.mfg_date:
                raise ValidationError('Expiry date must be after manufacturing date.')

    def action_mark_expired(self):
        today = date.today()
        for rec in self:
            if rec.expiry_date and rec.expiry_date <= today:
                rec.active = False

    def is_expired(self):
        today = date.today()
        return bool(self.expiry_date and self.expiry_date <= today)

    @api.model
    def _cron_check_and_notify(self):
        """Cron: find batches expiring in threshold and send mail"""
        threshold_days = 30
        today = fields.Date.context_today(self)
        notify_batches = self.search([('expiry_date','!=',False)])
        to_notify = []
        for b in notify_batches:
            # convert to date objects safely
            if b.expiry_date:
                delta = (fields.Date.to_date(b.expiry_date) - fields.Date.to_date(today)).days
                if delta <= threshold_days:
                    to_notify.append(b)
        # send mail per batch using template
        if to_notify:
            template = self.env.ref('alan_pharmacy_management.email_template_expiry_alert', raise_if_not_found=False)
            if template:
                for b in to_notify:
                    try:
                        template.with_context(batch_id=b.id).send_mail(b.id, force_send=True)
                    except Exception:
                        # don't raise cron exceptions
                        pass
