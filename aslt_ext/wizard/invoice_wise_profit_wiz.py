from odoo import api, fields, models, _


class InvoiceWiseProfitWiz(models.TransientModel):
    _name = 'aslt.invoice.wise.profit.wiz'
    _description = 'Invoice Wise Profit Wiz'

    date_from = fields.Date('Date From', default=fields.Date.context_today)
    date_to = fields.Date('Date To', default=fields.Date.context_today)

    def get_vendor_bills(self):
        return {'type': 'ir.actions.act_window_close'}

    def print_report(self):
        data = {
            'from_date': self.date_from,
            'date_to': self.date_to
        }
        return self.env.ref('aslt_ext.report_invoice_wise_profit').report_action(self, data=data)


class InvoiceWiseReportAbstract(models.AbstractModel):
    _name = 'report.aslt_ext.invoice_wise_profit_report'
    _description = "Invoice Wise Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        print("I'm Called")
        domain = [('move_type', '=', 'in_invoice')]
        if data.get('from_date'):
            domain.append(('invoice_date', '>=', data.get('from_date')))
            domain.append(('invoice_date', '<=', data.get('date_to')))
            docs = self.env['account.move'].search(domain)
            print(docs, "Record of Move after domain.")
            docs = docs.filtered(lambda item: 'BILL' in item.name)
            data.update()
            return {
                'doc_ids': docids,
                'doc_model': 'account.move',
                'docs': docs
            }
