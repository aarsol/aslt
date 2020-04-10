import pdb
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import common_timezones, timezone, utc
from dateutil import relativedelta

import time
from odoo import netsvc
from odoo.tools.safe_eval import safe_eval as eval
from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from odoo.exceptions import UserError, ValidationError


class HRLoans(models.Model):
	_name = 'hr.loans'
	_description = 'Loan Rule'

	name = fields.Char('Name', size=128, required=True)
	code = fields.Char('Code', size=64, required=True,)
	active = fields.Boolean('Active', help="If the active field is set to false, it will allow you to hide the Loan Rule without removing it.",default=True)
	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.user.company_id.id)
	amount_max = fields.Float('Maximum Amount', required=True,)
	shares_max = fields.Float('Maximum Shares', required=True,)
	amount_percentage = fields.Float('(%) of Basic', required=True, help='Share amount of Loan per Payslip should be in the threshold value',default=30.0)
	note = fields.Text('Description')
	journal_id = fields.Many2one('account.journal', 'Loan Journal', required=True)
	salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule')


class HRLoan(models.Model):
	_name = 'hr.loan'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_description = "Business Loan"

	def _compute_quota(self):
		self.amount_quota = self.amount/self.num_quotas

	@api.depends('amount','paid_amount')
	def _compute_remaining(self):
		self.remaining_debt = self.amount - self.paid_amount

	@api.depends('loan_line_ids.paid')		
	def _compute_amount(self):
		total_paid_amount = 0.00
		for loan in self:
			for line in loan.loan_line_ids:
				if line.paid == True:
					total_paid_amount +=line.paid_amount
			
			balance_amount =loan.amount - total_paid_amount
			self.total_amount = loan.amount
			self.balance_amount = balance_amount
			self.paid_amount = loan.amount - balance_amount	

	name = fields.Char("Description",required=True, readonly=True, states={'draft': [('readonly',False)]}, tracking=True)
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly',False)]}, tracking=True)
	loan_id = fields.Many2one('hr.loans', 'Loan Category', required=True, readonly=True, states={'draft': [('readonly',False)]}, tracking=True)
	amount = fields.Float('Loan Amount', digits=(16,2), required=True, readonly=True, states={'draft': [('readonly',False)]}, tracking=True)
	amount_quota = fields.Float(compute='_compute_quota', string='Share Amount', store=False)
	num_quotas = fields.Integer('Number of shares to pay', digits=(16,2), required=True,readonly=True, states={'draft': [('readonly',False)]})
	date_start = fields.Date('Start Date',readonly=True, states={'draft': [('readonly',False)]}, tracking=True)
	date_order = fields.Date('Date Order', readonly=True, states={'draft': [('readonly',False)]},default=lambda *a: time.strftime('%Y-%m-%d'), tracking=True)
	date_payment = fields.Date('Date of Payment',readonly=True, states={'draft': [('readonly',False)]}, tracking=True)
	paid_quotas = fields.Integer('Shares paid', digits=(16,2), readonly=True,default=0)
	paid_amount = fields.Float('Paid Amount', digits=(16,2), readonly=True,default=0.0)
	total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_amount')
	balance_amount = fields.Float(string="Balance Amount", compute='_compute_amount')
	loan_line_ids = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
	remaining_debt = fields.Float(compute='_compute_remaining', string='Balance', store=True)
	active = fields.Boolean('Active',default=True)
	note = fields.Text('Note')
	state = fields.Selection([('draft', 'Draft'), ('validate', 'Confirmed'), ('paid', 'Paid')], string='State', default='draft')
	#period_id = fields.many2one('account.period', 'Force Period',domain=[('state','<>','done')],states={'draft': [('readonly', False)]}, readonly=True, help="Keep empty to use the period of the validation(Payslip) date.")
	journal_id = fields.Many2one('account.journal',related='loan_id.journal_id', string="Loan Journal")
	debit_account_id = fields.Many2one('account.account','Debit Account',required=True,readonly=True)
	credit_account_id = fields.Many2one('account.account','Credit Account',required=True,readonly=True)
	code = fields.Char(related='loan_id.code', store=True, string="Code", tracking=True)
	move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
	payment_channel = fields.Selection([('bank','Bank'),('cash','Cash')], string='Payment Mode', default='bank')

	employee_code = fields.Char('Code', compute='compute_employee_branch', store=True, tracking=True)
	branch_id = fields.Many2one('odooschool.campus', string='Campus', compute='compute_employee_branch', store=True, tracking=True)
	city_id = fields.Many2one('odooschool.city', string='City', compute='compute_employee_branch', store=True, tracking=True)

	@api.depends('employee_id')
	def compute_employee_branch(self):
		for rec in self:
			rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
			rec.branch_id = rec.employee_id.branch_id and rec.employee_id.branch_id.id or False
			rec.city_id = rec.employee_id.branch_id and rec.employee_id.branch_id.city_id and rec.employee_id.branch_id.city_id.id or False

	def _check_dates(self):
		current_date = datetime.now().strftime('%Y-%m-%d')
		for loan in self:
			if loan.date_start < current_date or loan.date_payment:
				return False
		return True

	@api.model
	def create(self,vals):		
		loans = self.env['hr.loans'].browse(vals['loan_id'])
		employee = self.env['hr.employee'].browse(vals['employee_id'])

		if employee:
			if vals['amount'] <= 0 or vals['num_quotas'] <= 0:
				raise UserError('Amount of Loan and the number of Shares to pay should be Greater than Zero')

			if vals['amount'] > loans.amount_max:
				raise UserError(_('Amount of Loan for (%s) is greater than Allowed amount for (%s)') % (employee.name,loans.name))

			if vals['num_quotas'] > loans.shares_max:
				raise UserError(_('Number of Shares for (%s) is greater than Allowed Shares for (%s)') % (employee.name,loans.name))

			amount_quota = vals['amount'] / vals['num_quotas']
			if amount_quota > (employee.contract_id.wage * loans.amount_percentage / 100.0):
				raise UserError(_('The requested Loan Amount for  (%s) Exceed the (%s)%% of his Basic Salary (%s). The Loan cannot be registered') % (employee.name, loans.amount_percentage, employee.contract_id.wage))

		return super(HRLoan, self).create(vals)

	def loan_confirm(self):
		self.write({'state': 'validate'})

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('You can only delete Entries that are in draft state .'))
		return super(HRLoan, self).unlink()

	def loan_pay(self):
		#do accounting entries here
		move_pool = self.env['account.move']
		timenow = time.strftime('%Y-%m-%d')

		for loan in self:
			default_partner_id = loan.employee_id.address_home_id.id
			name = _('Loans To Mr. %s') % (loan.employee_id.name)
			move = {
				'narration': name,
				'date': timenow,
				'journal_id': loan.loan_id.journal_id.id,
			}

			amt = loan.amount
			partner_id = default_partner_id
			debit_account_id = loan.debit_account_id.id
			credit_account_id = loan.credit_account_id.id

			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0

			analytic_tags = self.env['account.analytic.tag']
			analytic_tags += self.employee_id.analytic_tag_id
			analytic_tags += self.employee_id.department_id.analytic_tag_id
			analytic_tags += self.employee_id.branch_id.analytic_tag_id
			analytic_tags += self.employee_id.city_id.analytic_tag_id
			analytic_tag_ids = [(6, 0, analytic_tags.ids)]

			if debit_account_id:
				debit_line = (0, 0, {
					'name': loan.loan_id.name,
					'date': timenow,
					'partner_id': partner_id,
					'account_id': debit_account_id,
					'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
					'debit': amt > 0.0 and amt or 0.0,
					'credit': amt < 0.0 and -amt or 0.0,
					'analytic_tag_ids': analytic_tag_ids,
				})
				line_ids.append(debit_line)
				debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

			if credit_account_id and not loan.payment_channel == 'cash':
				credit_line = (0, 0, {
					'name': loan.loan_id.name,
					'date': timenow,
					'partner_id': partner_id,
					'account_id': credit_account_id,
					'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
					'debit': amt < 0.0 and -amt or 0.0,
					'credit': amt > 0.0 and amt or 0.0,
					'analytic_tag_ids': analytic_tag_ids,
				})
				line_ids.append(credit_line)
				credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
							
			if credit_account_id and loan.payment_channel == 'cash':
				statement_rec = self.env['account.bank.statement'].search([('date','=',loan.date_order),('state','=','open')])
				if statement_rec:
					line_vals = ({
						'statement_id' : statement_rec.id,
						'name' : name,
						'journal_id' : 9,
						'company_id' : 1,
						'date' : loan.date_order,
						'account_id' : debit_account_id,
						'entry_date' : timenow,
						'amount': -amt,
					})
					statement_line = self.env['account.bank.statement.line'].create(line_vals)

					#Credit Entry
					credit_line = (0, 0, {
						'name': loan.loan_id.name,
						'date': timenow,
						'partner_id': partner_id,
						'account_id': credit_account_id,
						'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
						'debit': amt < 0.0 and -amt or 0.0,
						'credit': amt > 0.0 and amt or 0.0,
						'analytic_tag_ids': analytic_tag_ids,
					})
					line_ids.append(credit_line)
					credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

				else:
					raise UserError(_('There is no CashBook entry Opened for this Date. May be Cashbook Validated.'))
		
			move.update({'line_ids': line_ids})
			move_id = move_pool.create(move)
			self.write({'move_id': move_id.id, 'state': 'paid'})
			#move_id.post()
			self.compute_loan_line()
		return True

	def compute_loan_line(self):
		loan_line = self.env['hr.loan.line']
		input_obj = self.env['hr.emp.salary.inputs']
		
		loan_line.search([('loan_id','=',self.id)]).unlink()
		for loan in self:
			date_start_str = loan.date_payment
			counter = 1
			amount_per_time = loan.amount / loan.num_quotas
			for i in range(1, loan.num_quotas + 1):
				line_id = loan_line.create({
					'paid_date':date_start_str, 
					'paid_amount': amount_per_time,
					'employee_id': loan.employee_id.id,
					'loan_id':loan.id})
				
				## lines creation in hr_salary_inputs
				code = 'LOAN'
				input_id = input_obj.create({
					'employee_id': loan.employee_id.id,
					'name' : code,
					'amount' : amount_per_time,
					'state' : 'confirm',
					#'loan_line' : line_id.id,
					'input_id': 4,
					'date' : date_start_str,
					'employee_code' : loan.employee_id.code and loan.employee_id.code or '',
					'department_id' : loan.employee_id.department_id and loan.employee_id.department_id.id or False,
					'city_id': loan.employee_id.city_id and loan.employee_id.city_id.id or False,
					'branch_id': loan.employee_id.branch_id and loan.employee_id.branch_id.id or False,
					})
				counter += 1
				date_start_str = date_start_str + relativedelta.relativedelta(months =+1)
		return True


class HRLoanLine(models.Model):
	_name="hr.loan.line"
	_description = "HR Loan Request Line"
	
	paid_date = fields.Date(string="Payment Date", required=True)
	employee_id = fields.Many2one('hr.employee', string="Employee")
	paid_amount= fields.Float(string="Paid Amount", required=True)
	paid = fields.Boolean(string="Paid")
	notes = fields.Text(string="Notes")
	loan_id = fields.Many2one('hr.loan', string="Loan Ref.", ondelete='cascade')
	payroll_id = fields.Many2one('hr.payslip', string="Payslip Ref.")


class HRPayslipLoan(models.Model):
	_name = 'hr.payslip.loan'
	_description = 'Payslip Loan'
	_order = 'payslip_id, sequence'

	name = fields.Char('Description', size=256, required=True)
	payslip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=True, ondelete='cascade', index=True)
	sequence = fields.Integer('Sequence', required=True, index=True,default=10)
	code = fields.Char('Code', size=52, required=True, help="The code that can be used in the salary rules")
	amount = fields.Float('Amount', default='0.0',help="It is used in computation. For e.g. A rule for sales having 1% commission of basic salary for per product can defined in expression like result = inputs.SALEURO.amount * contract.wage*0.01.")
	contract_id = fields.Many2one('hr.contract', 'Contract', required=True, help="The contract for which applied this input")
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True, help="The Employe for which applied this input")


class HREmployee(models.Model):
	_inherit = 'hr.employee'

	loan_ids = fields.One2many('hr.loan', 'employee_id', 'Employee Loans')

