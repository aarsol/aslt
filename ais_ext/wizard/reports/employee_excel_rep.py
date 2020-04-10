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


class EmployeeDataExcelReport(models.TransientModel):
	_name = 'employee.data.excel.report'
	_description = 'Employee Data Report'

	city_ids = fields.Many2many('odooschool.city', 'employee_rep_cit_rel', 'employee_rep_id','city_id', string='City')
	branch_ids = fields.Many2many('odooschool.campus', 'employee_rep_campus_rel', 'employee_rep_id','branch_id', string='Campus')

	def make_excel(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Employee Data Report")
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
		worksheet.write_merge(0, 1, 0, 37, "ALHUDA International School Employee Data", style=style_title)

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
		col20.width = 256 * 20
		col21 = worksheet.col(21)
		col21.width = 256 * 20
		col22 = worksheet.col(22)
		col22.width = 256 * 20
		col23 = worksheet.col(23)
		col23.width = 256 * 20
		col24 = worksheet.col(24)
		col24.width = 256 * 20
		col25 = worksheet.col(25)
		col25.width = 256 * 20
		col26 = worksheet.col(26)
		col26.width = 256 * 20
		col27 = worksheet.col(27)
		col27.width = 256 * 20
		col28 = worksheet.col(28)
		col28.width = 256 * 20
		col29 = worksheet.col(29)
		col29.width = 256 * 20
		col30 = worksheet.col(30)
		col30.width = 256 * 20
		col31 = worksheet.col(31)
		col31.width = 256 * 20
		col32 = worksheet.col(32)
		col32.width = 256 * 20
		col33 = worksheet.col(33)
		col33.width = 256 * 30
		col34 = worksheet.col(34)
		col34.width = 256 * 20
		col35 = worksheet.col(35)
		col35.width = 256 * 20
		col36 = worksheet.col(36)
		col36.width = 256 * 20
		col37 = worksheet.col(37)
		col37.width = 256 * 40


		row = 2
		col = 0
		table_header = ['SR# No.', 'Code', 'Name','Father Name','CNIC','Mobile',
						'Phone','Email','Department','Designation','Date of Birth',
						'Gender','Marital Status','Address','Country','Branch','City','Joining Date',
						'Appointment Date','Confirmation Date','Basic Salary','Transport Allow',
						'Sp. Allowance','Experience Allow','Teacher Allow','Arrears','Extra Duty',
						'Co-ord Allow','House Rent','Medical Allowance','Utilities',
						'Income Tax','Advance Loan','Training / Donation Deduction','EOBI','ProbSecurity','LWP','Remarks']

		for i in range(38):
			worksheet.write(row, col, table_header[i], style=style_table_header)
			col += 1

		row +=1
		col = 0
		worksheet.write_merge(row, row, 0, 19, "Personal Information", style=style_title2)
		worksheet.write_merge(row, row, 20, 20, "", style=style_title2)
		worksheet.write_merge(row, row, 21, 30, "Allowances", style=style_title2)
		worksheet.write_merge(row, row, 31, 36, "Deductions", style=style_title2)
		worksheet.write_merge(row, row, 37, 37, "Deductions", style=style_title2)

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
				address = ''
				gender = ''
				remarks = ''
				wage = 0
				transport_id = False
				sp_id = False
				experience_id = False
				teacher_id = False
				arrears_id = False
				extra_id = False
				co_id = False
				house_id = False
				medical_id = False
				utility_id = False
				income_id = False
				loan_id = False
				training_id = False
				eobi_id = False
				prob_id = False
				lwp_id = False

				contract_id = self.env['hr.contract'].search([('employee_id','=',employee.id),('state','not in',('close','cancel'))])
				if contract_id:
					wage = contract_id.wage
					transport_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','TRAS')])
					sp_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','SPA')])
					experience_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','EXA')])
					teacher_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','TA')])
					arrears_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','ARS')])
					extra_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','EXTD')])
					co_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','COA')])
					house_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','HRA')])
					medical_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','MED')])
					utility_id = self.env['hr.emp.salary.allowances'].search([('contract_id','=',contract_id.id),('code','=','UTL')])
					income_id = self.env['hr.emp.salary.deductions'].search([('contract_id','=',contract_id.id),('code','=','INCTX')])
					loan_id = self.env['hr.emp.salary.deductions'].search([('contract_id','=',contract_id.id),('code','=','LOAN')])
					training_id = self.env['hr.emp.salary.deductions'].search([('contract_id','=',contract_id.id),('code','=','TDD')])
					eobi_id = self.env['hr.emp.salary.deductions'].search([('contract_id','=',contract_id.id),('code','=','EOBI')])
					prob_id = self.env['hr.emp.salary.deductions'].search([('contract_id','=',contract_id.id),('code','=','ProbSecurity')])
					lwp_id = self.env['hr.emp.salary.deductions'].search([('contract_id','=',contract_id.id),('code','=','LWP')])

				if not contract_id:
					remarks = 'No Salary Contract Found'

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
				worksheet.write(row, col, employee.code and employee.code or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, employee.name and employee.name or '', style=style_date_col2)
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
				worksheet.write(row, col, wage,style=style_date_col2)
				col += 1
				worksheet.write(row, col, transport_id and transport_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, sp_id and sp_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, experience_id and experience_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, teacher_id and teacher_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, arrears_id and arrears_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, extra_id and extra_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, co_id and co_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, house_id and house_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, medical_id and medical_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, utility_id and utility_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, income_id and income_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, loan_id and loan_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, training_id and training_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, eobi_id and eobi_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, prob_id and prob_id.amount or '', style=style_date_col2)
				col += 1
				worksheet.write(row, col,lwp_id and lwp_id.amount or  '', style=style_date_col2)
				col += 1
				worksheet.write(row, col, remarks, style=style_date_col2)
				col += 1

				col += 1
				sr += 1

		file_data = io.BytesIO()
		workbook.save(file_data)
		
		wiz_id = self.env['students.excel.report.save.wizard'].create({
			'data': base64.encodebytes(file_data.getvalue()),
			'name': 'Employee Data Report.xls'
		})
		return {
			'type': 'ir.actions.act_window',
			'name': 'Employee Data Report',
			'res_model': 'students.excel.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': wiz_id.id,
			'target': 'new',
			'context': self._context,
		}