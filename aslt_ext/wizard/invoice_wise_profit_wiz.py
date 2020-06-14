import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class InvoiceWiseProfitWiz(models.TransientModel):
    _name = 'aslt.invoice.wise.profit.wiz'
    _description = 'Invoice Wise Profit Wiz'


    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    def get_vendor_bills(self):

        return {'type': 'ir.actions.act_window_close'}


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'account.move',
            'form': data
        }
        return self.env.ref('aslt_ext.report_invoice_wise_profit').with_context(landscape=False).report_action(self, data=datas, config=False)
