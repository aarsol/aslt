# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    branch_id = fields.Many2one('res.branch')

    # def _query(self, fields={}, from_clause='', outer=''):
    #     fields['branch_id'] = ", s.branch_id as branch_id"
    #     return super(SaleReport, self)._query(fields, from_clause, outer)
