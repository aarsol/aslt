# -*- coding: utf-8 -*-
# Part of AmazeWorks Technologies

from odoo import models

class AccountMove(models.Model):
    # inherit the model for generate the customer invoice
    _inherit = 'account.move'

    def action_post(self):
        # Call the original (super) implementation of the 'action_post' method
        result = super(AccountMove, self).action_post()
        # Loop through invoices that are of type 'out_invoice'
        for invoice in self.filtered(lambda inv: inv.move_type == 'out_invoice'):
            # Call a custom method to generate analytic accounts from the invoice
            self._generate_analytic_account_from_invoice(invoice)
        # Return the result from the original 'action_post' method
        return result
    def _generate_analytic_account_from_invoice(self, invoice):
        # Search for an existing analytic account with the same name as the invoice
        existing_account = self.env['account.analytic.account'].search([('name', '=', invoice.name)], limit=1)
        # If an existing account is not found, create a new analytic account
        if not existing_account:
            analytic_account = self.env['account.analytic.account'].create({
                'name': invoice.name,
                'partner_id': invoice.partner_id.id
            })
            # Loop through invoice lines and associate the created account with each line
            for line in invoice.invoice_line_ids:
                # Set the analytic_distribution field to a dictionary with the created account
                line.analytic_distribution = {analytic_account.id: 100}





