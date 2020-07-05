import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
from odoo import http

import logging
_logger = logging.getLogger(__name__)

from io import StringIO
import io

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class InvoiceWiseProfitWiz(models.TransientModel):
    _name = 'aslt.invoice.wise.profit.wiz'
    _description = 'Invoice Wise Profit Wiz'


    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    def print_report(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Invoice Wise Profit Report")

        style_table_header_top = xlwt.easyxf("font:height 400; font: name Liberation Sans, bold on,color cyan_ega; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid;")
        style_table_header = xlwt.easyxf("font:height 270; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;")
        style_table_header2 = xlwt.easyxf("font:height 320; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; alignment: wrap True;")
        style_data_col = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")

        current_user = http.request.env.user
        company = ""
        if current_user and current_user.company_id:
            company = current_user.company_id.name

        length = 7
        worksheet.write_merge(0, 0, 0, length, company, style=style_table_header_top)
        worksheet.row(0).height = 256 * 3

        row_start = 1
        column_Start = 0
        worksheet.write_merge(row_start, row_start + 1, column_Start, column_Start+7, 'Invoice Wise Profit', style=style_table_header2)
        row_start += 2

        worksheet.write(row_start , column_Start , "Sr. No", style=style_table_header)
        worksheet.write(row_start, column_Start + 1, "Bill Number", style=style_table_header)
        worksheet.write(row_start, column_Start + 2, "Vendor", style=style_table_header)
        worksheet.write(row_start, column_Start + 3, "Amount", style=style_table_header)
        worksheet.write(row_start, column_Start + 4, "Invoice No", style=style_table_header)
        worksheet.write(row_start, column_Start + 5, "Customer", style=style_table_header)
        worksheet.write(row_start, column_Start + 6, "Amount", style=style_table_header)
        worksheet.write(row_start, column_Start + 7, "Difference", style=style_table_header)
        worksheet.row(3).height = 256 * 2
        worksheet.row(4).height = 256 * 2

        worksheet.col(column_Start + 0).width = 256 * 10
        worksheet.col(column_Start + 1).width = 256 * 22
        worksheet.col(column_Start + 2).width = 256 * 30
        worksheet.col(column_Start + 3).width = 256 * 12
        worksheet.col(column_Start + 4).width = 256 * 22
        worksheet.col(column_Start + 5).width = 256 * 30
        worksheet.col(column_Start + 6).width = 256 * 12
        worksheet.col(column_Start + 7).width = 256 * 20

        sale_orders = self.env['account.move'].search([('type', '=', 'in_invoice')])
        if self.date_from:
            sale_orders = sale_orders.filtered(lambda l: l.invoice_date >= self.date_from)
        if self.date_to:
            sale_orders = sale_orders.filtered(lambda l: l.invoice_date <= self.date_to)

        count = 0
        for rec in sale_orders:
            count += 1
            row_start += 1

            customer_amount = 0
            difference = rec.amount_total
            if rec.invoice_sale_id:
                difference = round (rec.invoice_sale_id.amount_total-rec.amount_total,2)
                customer_amount = round(rec.invoice_sale_id.amount_total,2)
            worksheet.write(row_start, column_Start, str(count), style=style_data_col)
            worksheet.write(row_start, column_Start + 1, rec.name, style=style_data_col)
            worksheet.write(row_start, column_Start + 2, rec.partner_id.name, style=style_data_col)
            worksheet.write(row_start, column_Start + 3, str(round(rec.amount_total,2)), style=style_data_col)
            worksheet.write(row_start, column_Start + 4, rec.invoice_sale_id.name or '-', style=style_data_col)
            worksheet.write(row_start, column_Start + 5, rec.invoice_sale_id.partner_id.name , style=style_data_col)
            worksheet.write(row_start, column_Start + 6, str(customer_amount) + " "  + rec.currency_id.name or "", style=style_data_col)
            worksheet.write(row_start, column_Start + 7, str(difference) + " " + rec.currency_id.name, style=style_data_col)

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['invoice.wise.profit.save.wizard'].create({
            'data': base64.encodestring(file_data.getvalue()),
            'name': 'Invoice-Wise-Profit.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice-Wise-Profit Sheet',
            'res_model': 'invoice.wise.profit.save.wizard',
            'view_mode': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }


    # def print_report(self):
    #     self.ensure_one()
    #     [data] = self.read()
    #     datas = {
    #         'ids': [],
    #         'model': 'account.move',
    #         'form': data
    #     }
    #     return self.env.ref('aslt_ext.report_invoice_wise_profit').with_context(landscape=False).report_action(self, data=datas, config=False)


class InvoiceWiseProfitWizSave(models.TransientModel):
    _name = "invoice.wise.profit.save.wizard"
    _description = 'Invoice Wise Profit Report Wizard'

    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)