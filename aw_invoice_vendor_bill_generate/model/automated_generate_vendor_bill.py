# your_module/cron/generate_vendor_bills.py
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models, fields

class GenerateVendorBills(models.Model):
    _inherit = 'account.move'
    _description = 'Generate Vendor Bills'
    vendor_bill_generated = fields.Boolean(string="Vendor Bill Generated", default=False)
    def generate_vendor_bill(self):
        # Get all analytic accounts
        analytic_accounts = self.env['account.analytic.account'].search([])

        for analytic_account in analytic_accounts:
            # Filter invoice lines based on conditions
            posted_invoice_lines = analytic_account.line_ids.filtered(lambda line:
                line.account_id and
                line.move_line_id.move_id.invoice_date >= datetime(2023, 4, 1).date() and  # 1- invoice_date >= 1-jan-2024
                line.move_line_id.move_id.payment_state == 'in_payment' and                       # 2- invoice status paid
                not line.move_line_id.move_id.vendor_bill_generated and         # 3- no previous vendor bill
                line.move_line_id.move_id.invoice_date + relativedelta(months=3) <= fields.Date.today())  # 4- invoice date 3 months ago

            if posted_invoice_lines:
                # Calculate total amount for the posted invoice lines
                total_amount = sum(posted_invoice_lines.mapped('amount'))

                # Calculate 2.5% donation
                donation_percentage = 2.5
                donation_amount = (donation_percentage / 100) * total_amount

                specific_vendor = self.env['res.partner'].search([('is_zakat_vendor', '=', True)], limit=1)
                vendor_bill_obj = self.env['account.move'].create({
                    'partner_id': specific_vendor.id,
                    'move_type': 'in_invoice',
                    'invoice_date': fields.Date.today(),
                    'ref': f"Vendor Bill for Analytic Account {analytic_account.name}",
                    'vendor_bill_generated': True  # Mark as vendor bill generated
                })

                donation_product = self.env['product.product'].search([('is_donation_product', '=', True)], limit=1)
                invoice_line_obj = self.env['account.move.line'].create({
                    'move_id': vendor_bill_obj.id,
                    'date_maturity': fields.Date.today(),
                    'quantity': 1,
                    'price_unit': max(0, donation_amount),
                    'product_id': donation_product.id,
                    'tax_ids': [(6, 0, [])],
                })
                vendor_bill_obj.action_post()
                # Mark original invoice as having a vendor bill generated
                for line in posted_invoice_lines:
                    line.move_line_id.move_id.vendor_bill_generated = True

        return True
