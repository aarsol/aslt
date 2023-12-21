from odoo import fields,models,api



class AccountMove(models.Model):
    _inherit = 'account.move'
    analytic_dist = fields.Char( string='Analytic',compute="_compute_analytic_account",
                                           store=True)

    @api.depends('invoice_line_ids.analytic_distribution')
    def _compute_analytic_account(self):
        for move in self:
            if move.invoice_line_ids and move.invoice_line_ids[0].analytic_distribution:
                analytic_accounts = move.invoice_line_ids[0].analytic_distribution
                for analytic_account_id, percentage in (analytic_accounts or {}).items():
                    analytic = self.env['account.analytic.account'].browse(int(analytic_account_id))
                    move.analytic_dist = analytic.name
