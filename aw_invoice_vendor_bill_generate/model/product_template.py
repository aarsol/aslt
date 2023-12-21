from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'product.template'
    is_donation_product = fields.Boolean(string="IS Donation Product?")