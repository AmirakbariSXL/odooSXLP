from odoo import models, fields

class AlanPharmaDoctor(models.Model):
    _name = 'alan.pharma.doctor'
    _description = 'Doctor'

    name = fields.Char(string='Name', required=True)
    image = fields.Image("Doctor Image")
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    specialization = fields.Char(string='Specialization')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    note = fields.Text(string='Notes')
    prescription_ids = fields.One2many('alan.pharma.prescription', 'doctor_id', string='Prescriptions')
