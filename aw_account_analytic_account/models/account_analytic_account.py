# -*- coding: utf-8 -*-
# Part of AmazeWorks Technologies

from odoo import api, fields, models

PAYMENT_STATE_SELECTION = [
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
]
class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'



    cost_percentage = fields.Float(
        string='Cost Percentage',
        
    )
    payment_state = fields.Selection(
        selection=PAYMENT_STATE_SELECTION,
        string="Payment Status",
    )

    invoice_user_id = fields.Many2one('res.users', 'Salesperson')

    # create field with the same name of existing field and set Default value in it

    #  in default variable call the function and set the value
    plan_id = fields.Many2one('account.analytic.plan', string='Plan', default=lambda self: self._set_default_plan_id())

    def _set_default_plan_id(self):
        #  default_plan_id work on account.analytic.plan and search in name field which value are Default
        default_plan_id = self.env['account.analytic.plan'].search([('name', '=', 'Default')], limit=1)
        # then return the value
        return default_plan_id

    
    @api.depends('line_ids.amount')
    def _compute_debit_credit_balance(self):
        # Call the original method to calculate the original balance
        super(AccountAnalyticAccount, self)._compute_debit_credit_balance()

        for record in self:
            if record.credit != 0 and record.debit != 0:
                record.cost_percentage = (record.debit / record.credit) * 100
            else:
                record.cost_percentage = 0.0
            account_move = self.env['account.move'].search([('name','=', record.display_name)], limit=1) or False
            if account_move:
                record.invoice_user_id = account_move.invoice_user_id.id
                record.payment_state = account_move.payment_state
