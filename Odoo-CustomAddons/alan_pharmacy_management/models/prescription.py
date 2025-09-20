from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AlanPharmaPrescriptionLine(models.Model):
    _name = 'alan.pharma.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one('alan.pharma.prescription', string='Prescription', ondelete='cascade')
    medicine_id = fields.Many2one('alan.pharma.medicine', string='Medicine', required=True)
    batch_id = fields.Many2one('alan.pharma.batch', string='Batch')
    dose = fields.Char(string='Dose')
    frequency = fields.Char(string='Frequency')
    duration = fields.Char(string='Duration')
    notes = fields.Text(string='Notes')
    qty = fields.Float(string='Quantity', default=1.0)

class AlanPharmaPrescription(models.Model):
    _name = 'alan.pharma.prescription'
    _description = 'Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Prescription Reference', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('alan.pharma.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('alan.pharma.doctor', string='Doctor')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    line_ids = fields.One2many('alan.pharma.prescription.line', 'prescription_id', string='Medicines')
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('dispensed','Dispensed')], string='Status', default='draft')
    note = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('alan.prescription') or 'New'
            vals['name'] = seq
        return super().create(vals)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            # schedule a simple activity (todo) for pharmacist
            rec.activity_schedule('mail.mail_activity_data_todo', summary='Confirm prescription')

    def action_dispense(self):
        for rec in self:
            for line in rec.line_ids:
                needed = line.qty
                batches = self.env['alan.pharma.batch'].search([
                    ('medicine_id', '=', line.medicine_id.id),
                    ('quantity', '>', 0),
                    ('active', '=', True)
                ], order='expiry_date')
                for b in batches:
                    if needed <= 0:
                        break
                    take = min(b.quantity, needed)
                    b.quantity = b.quantity - take
                    needed -= take
                if needed > 0:
                    raise ValidationError(f'Not enough stock for {line.medicine_id.name}')
            rec.state = 'dispensed'
            rec.message_post(body='Prescription dispensed')

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'
