from odoo import api, fields, models, _
from datetime import date, datetime, timedelta

import logging

_logger = logging.getLogger(__name__)

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


class AccountTaxReport(models.TransientModel):
    _name = 'account.tax.report'
    _description = 'Account Tax Report'

    date_from = fields.Date('From Date', default=fields.Date.today(), required=1)
    date_to = fields.Date('To Date', default=fields.Date.today(), required=1)

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Account Tax Report")
        style_title = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_table_header = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
        style_table_header2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;alignment: wrap True;")
        style_table_totals = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_date_col = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
        style_date_col2 = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")

        # col width
        col0 = worksheet.col(0)
        col0.width = 256 * 8
        col1 = worksheet.col(1)
        col1.width = 256 * 20
        col2 = worksheet.col(2)
        col2.width = 256 * 20
        col3 = worksheet.col(3)
        col3.width = 256 * 20
        col4 = worksheet.col(4)
        col4.width = 256 * 20
        col5 = worksheet.col(5)
        col5.width = 256 * 20
        col6 = worksheet.col(6)
        col6.width = 256 * 20
        col7 = worksheet.col(7)
        col7.width = 256 * 20
        col8 = worksheet.col(8)
        col8.width = 256 * 20
        col9 = worksheet.col(9)
        col9.width = 256 * 20
        col10 = worksheet.col(10)
        col10.width = 256 * 20

        current_time = fields.Datetime.now() + timedelta(hours=+5)
        worksheet.write_merge(0, 1, 0, 7,
                              'Tax Report from ' + self.date_from.strftime('%d-%m-%Y') + " To " + self.date_to.strftime(
                                  '%d-%m-%Y'), style=style_table_header2)
        row = 2
        col = 0

        table_header = ['SR# No.', 'Invoice Ref', 'Invoice Date', 'Payment Ref', 'Payment Date', 'Invoice Amount',
                        'Payment Amount', 'Tax Amount']
        for i in range(8):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1
        payments = self.env['account.payment'].search([('date', '>=', self.date_from),
                                                       ('date', '<=', self.date_to),
                                                       ('payment_type', '=', 'inbound'),
                                                       ('partner_type', '=', 'customer')], order='date')
        sr = 1
        total_tax = 0

        if payments:
            for payment in payments:
                # if payment.invoice_ids:
                # Changes By Fahad
                if payment.reconciled_invoice_ids:
                    # for invoice in payment.invoice_ids:
                    for invoice in payment.reconciled_invoice_ids:
                        if invoice.amount_tax > 0:
                            row += 1
                            col = 0
                            total_tax += invoice.amount_tax
                            worksheet.write(row, col, sr, style=style_date_col2)
                            col += 1
                            worksheet.write(row, col, invoice.name, style=style_date_col2)
                            col += 1
                            worksheet.write(row, col, invoice.invoice_date.strftime("%d-%m-%Y"), style=style_date_col2)
                            col += 1
                            worksheet.write(row, col, payment.name, style=style_date_col2)
                            col += 1
                            worksheet.write(row, col, payment.date.strftime("%d-%m-%Y"), style=style_date_col2)
                            col += 1
                            worksheet.write(row, col, invoice.amount_total, style=style_date_col2)
                            col += 1
                            worksheet.write(row, col, payment.amount, style=style_date_col2)
                            col += 1
                            worksheet.write(row, col, invoice.amount_tax, style=style_date_col2)
                            col += 1
                            sr += 1

            row += 1
            col = 0
            worksheet.write(row, col, '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, total_tax, style=style_date_col2)
            col += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['account.excel.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Tax Report.xls'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tax Report',
            'res_model': 'account.excel.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }


class AccountExcelReportSaveWizard(models.TransientModel):
    _name = "account.excel.report.save.wizard"
    _description = 'Account Report Save Wizard'

    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)
