from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AlanPharmaMedicine(models.Model):
    _name = 'alan.pharma.medicine'
    _description = 'Medicine'
    _order = 'name'

    name = fields.Char(string='Name', required=True, index=True)
    image = fields.Image("Medicine Image")
    default_code = fields.Char(string='Internal Reference')
    barcode = fields.Char(string='Barcode')
    medicine_type = fields.Selection(
        [('tablet','Tablet'),('syrup','Syrup'),('injection','Injection'),('ointment','Ointment'),('other','Other')],
        string='Type', default='tablet')
    product_id = fields.Many2one('product.product', string='Product', ondelete='set null')
    category = fields.Char(string='Category')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    total_quantity = fields.Float(string='Total Quantity (According to Batches)', compute='_compute_total_quantity', store=True)
    next_expiry = fields.Date(string='Next Expiry', compute='_compute_next_expiry', store=True)

    batch_ids = fields.One2many('alan.pharma.batch', 'medicine_id', string='Batches')

    @api.depends('batch_ids', 'batch_ids.quantity')
    def _compute_total_quantity(self):
        for rec in self:
            rec.total_quantity = sum(batch.quantity for batch in rec.batch_ids)

    @api.depends('batch_ids', 'batch_ids.expiry_date')
    def _compute_next_expiry(self):
        for rec in self:
            expiries = [b.expiry_date for b in rec.batch_ids if b.expiry_date]
            rec.next_expiry = min(expiries) if expiries else False

    @api.constrains('product_id')
    def _check_product(self):
        for rec in self:
            if rec.product_id and rec.product_id.type == 'service':
                raise ValidationError('Product linked to medicine must be storable (not service).')
