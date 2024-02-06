from odoo import models, fields, api
class AcountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    def action_create_payments(self):
        if self.payment_type == 'inbound':
            # Check if payment type is 'Receive Money', the vendor is a zakat vendor, and the donation product exists

            # add the payment amount by 5%
            # add_amount = self.amount / 105
            result = self.amount / 105
            # Calculate 2.5% fee on the reduced amount
            fee_amount = result * 2.5
            # Create a vendor bill
            specific_vendor = self.env['res.partner'].search([('is_zakat_vendor', '=', 'True')],
                                                             limit=1)
            # Create a vendor bill
            vendor_bill_obj = self.env['account.move'].create({
                'partner_id': specific_vendor.id,
                'move_type': 'in_invoice',
                'invoice_date': self.payment_date,
            })
            # Create a product line on the vendor bill with the calculated fee as the unit price
            donation_product = self.env['product.product'].search(
                [('name', '=', 'Donation'), ('is_donation_product', '=', True)], limit=1)
            invoice_line_obj = self.env['account.move.line'].create({
                'move_id': vendor_bill_obj.id,
                'date_maturity': self.payment_date,
                'quantity': 1,
                'price_unit': fee_amount,
                'product_id': donation_product.id,
                'tax_ids': [(6, 0, [])],
            })
            vendor_bill_obj.action_post()
            # Mark the payment as confirmed
            return super(AcountPaymentRegister, self).action_create_payments()
        else:
            # If the conditions are not met, proceed with the default behavior
            return super(AcountPaymentRegister, self).action_create_payments()

