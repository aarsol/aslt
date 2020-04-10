from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
from datetime import date
from datetime import datetime, timedelta,time
from dateutil import relativedelta
from odoo.exceptions import UserError
from pytz import timezone, utc

import logging
_logger = logging.getLogger(__name__)
from io import StringIO,BytesIO
import io
import pdb

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


class NoContractEmployeeReport(models.TransientModel):
	_name = 'no.contract.employee.report'
	_description = 'Employee Having no Contract Report'

	city_ids = fields.Many2many('odooschool.city', 'no_contract_rep_cit_rel', 'no_contract_rep_id','city_id', string='City')
	branch_ids = fields.Many2many('odooschool.campus', 'no_contract_rep_campus_rel', 'no_contract_rep_id','branch_id', string='Campus')

	def make_excel(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("No Contract Employee Report")
		style_title = xlwt.easyxf(
			"font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid,fore_colour periwinkle;")
		style_title1 = xlwt.easyxf(
			"font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;")
		style_title2 = xlwt.easyxf(
			"font:height 210; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid,fore_colour periwinkle;")
		style_table_header = xlwt.easyxf(
			"font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid,fore_colour silver_ega;")
		style_ot_totals = xlwt.easyxf(
			"font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left; pattern: pattern solid, fore_colour red;;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour rose;")
		style_date_col2 = xlwt.easyxf(
			"font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		worksheet.write_merge(0, 1, 0, 20, "ALHUDA International School Employee Data", style=style_title)

		# col width
		col0 = worksheet.col(0)
		col0.width = 256 * 8
		col1 = worksheet.col(1)
		col1.width = 256 * 20
		col2 = worksheet.col(2)
		col2.width = 256 * 35
		col3 = worksheet.col(3)
		col3.width = 256 * 25
		col4 = worksheet.col(4)
		col4.width = 256 * 25
		col5 = worksheet.col(5)
		col5.width = 256 * 20
		col6 = worksheet.col(6)
		col6.width = 256 * 20
		col7 = worksheet.col(7)
		col7.width = 256 * 20
		col8 = worksheet.col(8)
		col8.width = 256 * 25
		col9 = worksheet.col(9)
		col9.width = 256 * 20
		col10 = worksheet.col(10)
		col10.width = 256 * 20
		col11 = worksheet.col(11)
		col11.width = 256 * 20
		col12 = worksheet.col(12)
		col12.width = 256 * 20
		col13 = worksheet.col(13)
		col13.width = 256 * 25
		col14 = worksheet.col(14)
		col14.width = 256 * 25
		col15 = worksheet.col(15)
		col15.width = 256 * 20
		col16 = worksheet.col(16)
		col16.width = 256 * 20
		col17 = worksheet.col(17)
		col17.width = 256 * 20
		col18 = worksheet.col(18)
		col18.width = 256 * 20
		col19 = worksheet.col(19)
		col19.width = 256 * 20
		col20 = worksheet.col(20)
		col20.width = 256 * 30

		row = 2
		col = 0
		table_header = ['SR# No.', 'Code', 'Name','Father Name','CNIC','Mobile','Phone','Email','Department','Designation','Date of Birth',
						'Gender','Marital Status','Address','Country','Branch','City','Joining Date','Appointment Date','Confirmation Date','Remarks']

		for i in range(21):
			worksheet.write(row, col, table_header[i], style=style_table_header)
			col += 1

		employees = False
		if self.city_ids and self.branch_ids:
			employees = self.env['hr.employee'].search([('city_id','in',self.city_ids.ids),('branch_id', 'in', self.branch_ids.ids)])
		if not employees and self.city_ids:
			employees = self.env['hr.employee'].search([('city_id', 'in', self.city_ids.ids)])
		if not employees and self.branch_ids:
			employees = self.env['hr.employee'].search([('branch_id','in',self.branch_ids.ids)])

		if not employees and not self.branch_ids and not self.city_ids:
			employees = self.env['hr.employee'].search([],order="branch_id")

		if employees:
			sr = 1
			for employee in employees:
				contract_id = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('state', 'not in', ('close', 'cancel'))])
				if not contract_id:
					address = ''
					gender = ''
					remarks = 'Employee Salary Contract Not Found'

					if employee.street:
						address = address + employee.street
					if employee.street2:
						address = address + " " + employee.street2
					if employee.city:
						address = address + " " + employee.city

					if employee.gender == 'female':
						gender = 'Female'
					if employee.gender == 'male':
						gender = 'Male'

					row += 1
					col = 0
					worksheet.write(row, col, sr, style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.code and  employee.code or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.name and  employee.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.father_name and employee.father_name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.cnic and employee.cnic or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.mobile_phone and employee.mobile_phone or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.work_phone and employee.work_phone or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col,employee.work_email and employee.work_email or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col,employee.department_id and employee.department_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.job_id and employee.job_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.birthday and str(employee.birthday) or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, gender,style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.marital and employee.marital or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, address, style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.country_id and employee.country_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.branch_id and employee.branch_id.name or '',style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.city_id and employee.city_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col,employee.joining_date and str(employee.joining_date) or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.appointment_date and str(employee.appointment_date) or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, employee.confirmation_date and str(employee.confirmation_date) or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, remarks, style=style_date_col2)
					col += 1

					sr += 1

		file_data = io.BytesIO()
		workbook.save(file_data)
		
		wiz_id = self.env['students.excel.report.save.wizard'].create({
			'data': base64.encodebytes(file_data.getvalue()),
			'name': 'Employee Having No Contract Data.xls'
		})
		return {
			'type': 'ir.actions.act_window',
			'name': 'Employee Having No Contract Data Report',
			'res_model': 'students.excel.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': wiz_id.id,
			'target': 'new',
			'context': self._context,
		}