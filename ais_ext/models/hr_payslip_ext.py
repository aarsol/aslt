from datetime import date, datetime, time
from collections import defaultdict
from odoo.tools import date_utils
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError,UserError
from odoo.tools.misc import format_date
import pdb
import pytz
import logging
_logger = logging.getLogger(__name__)


class HRPayslip(models.Model):
    _inherit='hr.payslip'

    employee_code = fields.Char('Code', compute='compute_employee_branch', store=True)
    branch_id = fields.Many2one('odooschool.campus', string='Campus', compute='compute_employee_branch', store=True)
    city_id = fields.Many2one('odooschool.city', string='City', compute='compute_employee_branch', store=True)
    salary_transfer_mode = fields.Selection([('Cash','Cash'),('Bank','Bank'),('Cheque','Cheque')], string="Salary Transfer Mode",compute='compute_employee_branch', store=True)
    bank_account_title = fields.Char('Account Title', compute='compute_bank_info', store=True)
    bank_account_no = fields.Char('Account No',compute='compute_bank_info', store=True)
    bank_id = fields.Many2one('ais.bank', 'Bank',compute='compute_bank_info', store=True)

    @api.depends('employee_id')
    def compute_employee_branch(self):
        for rec in self:
            if rec.employee_id.salary_transfer_mode:
                rec.salary_transfer_mode = rec.employee_id.salary_transfer_mode and rec.employee_id.salary_transfer_mode or ''
            rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
            rec.branch_id = rec.employee_id.branch_id and rec.employee_id.branch_id.id or False
            rec.city_id = rec.employee_id.branch_id and rec.employee_id.branch_id.city_id and rec.employee_id.branch_id.city_id.id or False

    @api.depends('salary_transfer_mode')
    def compute_bank_info(self):
        for rec in  self:
            if rec.employee_id.salary_transfer_mode == 'Bank':
                rec.bank_id = rec.employee_id.bank_id and rec.employee_id.bank_id.id or False,
                rec.bank_account_title = rec.employee_id.bank_account_title and rec.employee_id.bank_account_title or ''
                rec.bank_account_no = rec.employee_id.bank_account_no and rec.employee_id.bank_account_no or ''
            else:
                rec.bank_id = False
                rec.bank_account_title = ''
                rec.bank_account_no = ''


class HREmpSalaryInputs(models.Model):
    _inherit = "hr.emp.salary.inputs"

    # NEED TO SHIFT THIS IN THE AIS EXT
    employee_code = fields.Char('Code', compute='compute_employee_data', store=True)
    branch_id = fields.Many2one('odooschool.campus', string='Campus', compute='compute_employee_data', store=True)
    city_id = fields.Many2one('odooschool.city', string='City', compute='compute_employee_data', store=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='compute_employee_data', store=True)

    @api.depends('employee_id')
    def compute_employee_data(self):
        for rec in self:
            rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
            rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
            rec.branch_id = rec.employee_id.branch_id and rec.employee_id.branch_id.id or False
            rec.city_id = rec.employee_id.branch_id and rec.employee_id.branch_id.city_id and rec.employee_id.branch_id.city_id.id or False

