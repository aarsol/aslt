from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError


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


class SalaryReport(models.TransientModel):
	_name = 'employee.salary.report'
	_description = 'Employee Salary Report'

	city_ids = fields.Many2many('odooschool.city', 'emp_salary_rep_cit_rel', 'salary_rep_id','city_id', string='City')
	branch_ids = fields.Many2many('odooschool.campus', 'emp_salary_rep_campus_rel', 'salary_rep_id','branch_id', string='Campus')
	date_from = fields.Date("From Date",default=lambda self: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date("To Date",default=lambda self: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])

	def get_payslip_working_days(self, payslip_id=None, code=None):
		worked_day_obj = self.env['hr.payslip.worked_days']
		worked_day_id = worked_day_obj.search([('payslip_id', '=', payslip_id), ('code', '=', code)])
		return worked_day_id.number_of_days

	def get_payslip_lines(self, payslip_id, line_type=None, code=None):
		payslip_line_obj = self.env['hr.payslip.line']
		payslip_input_obj = self.env['hr.payslip.input']
		amount = 0
		if line_type == 'payslip_line':
			payslip_line_id = payslip_line_obj.search([('slip_id', '=', payslip_id), ('code', '=', code)])
			amount = payslip_line_id.total or 0
		if line_type == 'input_line':
			input_id = payslip_input_obj.search([('payslip_id', '=', payslip_id), ('code', '=', code)])
			amount = input_id.amount or 0
		return amount

	def get_deduction(self, payslip):
		deduction = 0
		deduction_lines = self.env['hr.payslip.line'].search([('category_id', '=', 4), ('slip_id', '=', payslip)])
		for line in deduction_lines:
			deduction = line.total + deduction

		return deduction

	def make_excel(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Employee Salary Report")
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
		worksheet.write_merge(0, 1, 0, 33, "ALHUDA International School Salary Report From " + str(self.date_from) + " To " + str(self.date_to), style=style_title)

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


		row = 2
		col = 0
		table_header = ['SR#', 'Code', 'Name','Father Name','CNIC','Department','Designation','Branch','City','Joining Date','Appointment Date','Confirmation Date',
						'Basic Salary','Transport Allow','Sp. Allowance','Experience Allow','Teacher Allow','Arrears','Extra Duty','Co-ord Allow','House Rent','Medical Allowance','Utilities','Total Allowances','Gross Salary',
						'Income Tax','Advance Loan','Training / Donation Deduction','EOBI','ProbSecurity','LWP','Total Deductions','NET Salary','Remarks']

		for i in range(34):
			worksheet.write(row, col, table_header[i], style=style_table_header)
			col += 1

		row +=1
		col = 0
		worksheet.write_merge(row, row, 0, 11, "Personal Information", style=style_title2)
		worksheet.write_merge(row, row, 12, 12, "", style=style_title2)
		worksheet.write_merge(row, row, 13, 22, "Allowances", style=style_title2)
		worksheet.write_merge(row, row, 23, 23, "", style=style_title2)
		worksheet.write_merge(row, row, 24, 24, "", style=style_title2)
		worksheet.write_merge(row, row, 25, 31, "Deductions", style=style_title2)
		worksheet.write_merge(row, row, 32, 32, "", style=style_title2)
		worksheet.write_merge(row, row, 33, 33, "", style=style_title2)

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
			total_basic = 0
			total_transport = 0
			total_sp = 0
			total_exp = 0
			total_teacher = 0
			total_arrears = 0
			total_extra = 0
			total_co = 0
			total_house_rent = 0
			total_medical =0
			total_utility = 0
			total_allowances = 0
			total_gross = 0

			total_tax = 0
			total_loan = 0
			total_tdd = 0
			total_eobi = 0
			total_prob = 0
			total_twp = 0
			total_deductions = 0
			total_net = 0


			payslips = self.env['hr.payslip'].search([('employee_id','in',employees.ids),('date_from','>=',self.date_from),('date_to','<=',self.date_to)])

			if payslips:
				sr = 1
				for payslip in payslips:
					remarks = ''

					total_basic = total_basic + self.get_payslip_lines(payslip.id,'payslip_line','BASIC')
					total_transport = total_transport + self.get_payslip_lines(payslip.id,'payslip_line','TRA')
					total_sp = total_sp + self.get_payslip_lines(payslip.id,'payslip_line','SPA')
					total_exp = total_exp + self.get_payslip_lines(payslip.id,'payslip_line','EXA')
					total_teacher = total_teacher + self.get_payslip_lines(payslip.id,'payslip_line','TA')
					total_arrears = total_arrears + self.get_payslip_lines(payslip.id,'payslip_line','ARS')
					total_extra = total_extra + self.get_payslip_lines(payslip.id,'payslip_line','EXTD')
					total_co = total_co + self.get_payslip_lines(payslip.id,'payslip_line','COA')
					total_house_rent = total_house_rent + self.get_payslip_lines(payslip.id,'payslip_line','HRA')
					total_medical = total_medical + self.get_payslip_lines(payslip.id,'payslip_line','MED')
					total_utility = total_utility + self.get_payslip_lines(payslip.id,'payslip_line','UTL')
					total_allowances = total_allowances + 0
					total_gross = total_gross + self.get_payslip_lines(payslip.id,'payslip_line','GROSS')

					total_tax = total_tax + self.get_payslip_lines(payslip.id,'payslip_line','INCTX')
					total_loan = total_loan + self.get_payslip_lines(payslip.id,'payslip_line','LOAN')
					total_tdd = total_tdd + self.get_payslip_lines(payslip.id,'payslip_line','TDD')
					total_eobi = total_eobi + self.get_payslip_lines(payslip.id,'payslip_line','EOBI')
					total_prob = total_prob + self.get_payslip_lines(payslip.id,'payslip_line','ProbSecurity')
					total_twp = total_twp + self.get_payslip_lines(payslip.id,'payslip_line','LWP')
					total_deductions = total_deductions + 0
					total_net = total_net + self.get_payslip_lines(payslip.id,'payslip_line','NET')

					row += 1
					col = 0
					worksheet.write(row, col, sr, style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.code and payslip.employee_id.code or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.name and payslip.employee_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.father_name and payslip.employee_id.father_name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.cnic and payslip.employee_id.cnic or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.department_id and payslip.employee_id.department_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.job_id and payslip.employee_id.job_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col,payslip.employee_id.branch_id and payslip.employee_id.branch_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col,payslip.employee_id.city_id and payslip.employee_id.city_id.name or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col,payslip.employee_id.joining_date and str(payslip.employee_id.joining_date) or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.appointment_date and str(payslip.employee_id.appointment_date) or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, payslip.employee_id.confirmation_date and str(payslip.employee_id.confirmation_date) or '', style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','BASIC'),style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','TRA'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','SPA'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','EXA'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','TA'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','ARS'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','EXTD'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','COA'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','HRA'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','MED'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','UTL'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, '',style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','GROSS'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','INCTX'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','LOAN'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','TDD'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','EOBI'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id,'payslip_line','LWP'), style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id, 'payslip_line', 'ProbSecurity'),style=style_date_col2)
					col += 1
					worksheet.write(row, col, '',style=style_date_col2)
					col += 1
					worksheet.write(row, col, self.get_payslip_lines(payslip.id, 'payslip_line', 'NET'),style=style_date_col2)
					col += 1
					worksheet.write(row, col, remarks, style=style_date_col2)
					col += 1
					sr += 1

				row +=1
				worksheet.write_merge(row, row, 0, 11, "", style=style_title2)
				worksheet.write_merge(row, row, 12, 12, total_basic, style=style_title2)
				worksheet.write_merge(row, row, 13, 13, total_transport, style=style_title2)
				worksheet.write_merge(row, row, 14, 14, total_sp, style=style_title2)
				worksheet.write_merge(row, row, 15, 15, total_exp, style=style_title2)
				worksheet.write_merge(row, row, 16, 16, total_teacher, style=style_title2)
				worksheet.write_merge(row, row, 17, 17, total_arrears, style=style_title2)
				worksheet.write_merge(row, row, 18, 18, total_extra, style=style_title2)
				worksheet.write_merge(row, row, 19, 19, total_co, style=style_title2)
				worksheet.write_merge(row, row, 20, 20, total_house_rent, style=style_title2)
				worksheet.write_merge(row, row, 21, 21, total_medical, style=style_title2)
				worksheet.write_merge(row, row, 22, 22, total_utility, style=style_title2)
				worksheet.write_merge(row, row, 23, 23, total_allowances, style=style_title2)
				worksheet.write_merge(row, row, 24, 24, total_gross, style=style_title2)

				worksheet.write_merge(row, row, 25, 25, total_tax, style=style_title2)
				worksheet.write_merge(row, row, 26, 26, total_loan, style=style_title2)
				worksheet.write_merge(row, row, 27, 27, total_tdd, style=style_title2)
				worksheet.write_merge(row, row, 28, 28, total_eobi, style=style_title2)
				worksheet.write_merge(row, row, 29, 29, total_prob, style=style_title2)
				worksheet.write_merge(row, row, 30, 30, total_twp, style=style_title2)
				worksheet.write_merge(row, row, 31, 31, total_deductions, style=style_title2)
				worksheet.write_merge(row, row, 32, 32, total_net, style=style_title2)
				worksheet.write_merge(row, row, 33, 33, "", style=style_title2)

		file_data = io.BytesIO()
		workbook.save(file_data)
		
		wiz_id = self.env['students.excel.report.save.wizard'].create({
			'data': base64.encodebytes(file_data.getvalue()),
			'name': 'Employee Salary Report.xls'
		})
		return {
			'type': 'ir.actions.act_window',
			'name': 'Employee Salary Report',
			'res_model': 'students.excel.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': wiz_id.id,
			'target': 'new',
			'context': self._context,
		}