from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        if self.payment_type == 'inbound':

            # add the payment amount by 5%
            # add_amount = self.amount * 0.05
            result = self.amount / 105
            # Calculate 2.5% fee on the reduced amount
            fee_amount = result * 2.5
            # Create a vendor bill
            specific_vendor = self.env['res.partner'].search([('is_zakat_vendor','=','True')], limit=1)
            # Create a vendor bill
            vendor_bill_obj = self.env['account.move'].create({
                'partner_id': specific_vendor.id,
                'move_type': 'in_invoice',
                'invoice_date': self.date,
            })
            # Create a product line on the vendor bill with the calculated fee as the unit price
            donation_product = self.env['product.product'].search([('name', '=', 'Donation'), ('is_donation_product', '=', True)], limit=1)
            invoice_line_obj = self.env['account.move.line'].create({
                'move_id': vendor_bill_obj.id,
                'date_maturity': self.date,
                'quantity': 1,
                'price_unit': fee_amount,
                'product_id': donation_product.id,
                'tax_ids': [(6, 0, [])],
            })
            vendor_bill_obj.action_post()
            # Mark the payment as confirmed
            return super(AccountPayment, self).action_post()
        else:
            # If the conditions are not met, proceed with the default behavior
            return super(AccountPayment, self).action_post()








# from odoo import models, fields
# from odoo.exceptions import UserError
#
# class CustomInvoiceVendorBill(models.Model):
#     # _inherit = 'account.move'
#     _inherit = 'account.payment'
#     payment_method_id = fields.Many2one('account.payment.method', string='Payment Method')
#
#     # has_vendor_bill = fields.Boolean(string='Has Vendor Bill', compute='_compute_has_vendor_bill')
#     # vendor_bill_ids = fields.One2many('account.payment', 'invoice_origin', string='Vendor Bills', readonly=True)
#     def action_post(self):
#         # Call the parent method first
#         super(CustomInvoiceVendorBill, self).action_post()
#
#         # Find the 'purchase' type journal
#         purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
#         if not purchase_journal:
#             raise UserError("No purchase journal found")
#
#         # Create a new vendor bill (account.payment) with the necessary details and use the 'purchase' journal
#         vendor_bill = self.env['account.payment'].create({
#             'payment_type': 'inbound',  # Adjust the payment type as needed
#             'journal_id': purchase_journal.id,
#             'payment_method_id': self.payment_method_id.id,
#             'partner_id': self.partner_id.id,
#             # 'amount': self.amount,  # You may need to adjust the amount based on your requirements
#         })
#
#         # Calculate the surcharge as 2.5% of the amount of the invoice
#         surcharge = self.amount * 0.025
#
#         # Set the total amount with the surcharge
#         vendor_bill.amount = self.amount + surcharge
#
#         # Add the desired product line to the vendor bill with the surcharge
#         product_id = self.env['product.product'].search([('name', '=', 'Donation')], limit=1)
#         if product_id:
#             vendor_bill.write({
#                 'invoice_line_ids': [(0, 0, {
#                     'product_id': product_id.id,
#                     'name': product_id.name,
#                     'quantity': 1,
#                     'price_unit': surcharge,
#                 })]
#             })
#     # def action_view_vendor_bills(self):
#     #         vendor_bills = self.mapped('vendor_bill_ids')
#     #         action = self.env.ref('account.action_move_in_invoice_type').read()[0]
#     #         if len(vendor_bills) > 1:
#     #             action['domain'] = [('id', 'in', vendor_bills.ids)]
#     #         elif len(vendor_bills) == 1:
#     #             action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
#     #             action['res_id'] = vendor_bills[0].id
#     #         else:
#     #             action = {'type': 'ir.actions.act_window_close'}
#     #         return action
#     # def _compute_has_vendor_bill(self):
#     #     for invoice in self:
#     #         invoice.has_vendor_bill = bool(invoice.vendor_bill_ids)
#
