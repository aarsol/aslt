from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'res.partner'
    is_zakat_vendor = fields.Boolean(string="IS Zakat Vendor?")