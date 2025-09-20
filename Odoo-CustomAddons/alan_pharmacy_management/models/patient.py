from odoo import models, fields

class AlanPharmaPatient(models.Model):
    _name = 'alan.pharma.patient'
    _description = 'Patient'

    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    date_of_birth = fields.Date(string='Date of Birth')
    blood_group = fields.Selection([('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-')], string='Blood Group')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Other')], string='Gender')
    prescription_ids = fields.One2many('alan.pharma.prescription', 'patient_id', string='Prescriptions')
