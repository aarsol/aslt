import pdb
from odoo import api, fields, models, _
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
import pdb

_logger = logging.getLogger(__name__)


class InvoiceWiseProfitReport(models.AbstractModel):
    _name = 'report.aslt_ext.invoice_wise_profit_report'
    _description = 'Invoice Wise Profit Report'

    @api.model
    def _get_report_values(self, docsid, data=None):

        date_from = data['form']['date_from'] or False
        date_to = data['form']['date_to'] or False
        current_user = self.env.user

        sale_orders = self.env['account.move'].search([('type','=','in_invoice')])
        if date_from:
            sale_orders = sale_orders.filtered(lambda l: str(l.invoice_date) >= date_from)
        if date_to:
            sale_orders = sale_orders.filtered(lambda l: str(l.invoice_date) <= date_to)

        report = self.env['ir.actions.report']._get_report_from_name('aslt_ext.invoice_wise_profit_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'sale_orders': sale_orders or False,
            'branch': current_user.company_id or current_user.branch_id or False,
            'date_from': date_from or False,
            'date_to': date_to or False,
            # 'company': current_user.company_id or False,

        }
        return docargs
