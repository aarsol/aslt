from datetime import date, datetime, time
from collections import defaultdict
from odoo.tools import date_utils
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError,UserError
import pdb
import logging
_logger = logging.getLogger(__name__)


class HREmployeeExitForm(models.Model):
    _name = 'hr.employee.exit.form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Employee Exit Form"

    name = fields.Char('Name',tracking=True)
    employee_id = fields.Many2one('hr.employee','Employee',tracking=True)
    employee_code = fields.Char('Employee Code', tracking=True)
    cnic = fields.Char('CNIC', tracking=True)
    employee_father = fields.Char('Father Name')
    department_id = fields.Many2one('hr.department','Department',tracking=True)
    job_id = fields.Many2one('hr.job','Designation', tracking=True)
    city_id = fields.Many2one('odooschool.city','City')
    branch_id = fields.Many2one('odooschool.campus','Branch')
    joining_date = fields.Date('Joining Date')
    leaving_date = fields.Date('End Date')
    reason = fields.Selection([('Resignation','Resignation'),
                               ('Termination','Termination'),
                               ('Contract Expiry Period','Expiry of Contract Period'),
                               ('Others','Others')], string='Reason For Clearing',tracking=True)
    other_reason = fields.Text('Other Reason', placeholder="Please Specify Reason...")

    #Employee Department
    keys_handover = fields.Boolean('Keys Handover')
    officer_equipment = fields.Boolean('Officer Equipments')
    stationery_handover = fields.Boolean('Stationery Handover')
    completed_task_handover = fields.Boolean('Completed tasks and files handover')
    manual_books = fields.Boolean('Manuals And Books')
    important_matters = fields.Text('Detail of Important Matters Pending')
    file_reports_detail = fields.Text('File and Reports Detail')
    computer_data_detail = fields.Text('Compute Data Detail')

    #Library Department
    library_status = fields.Boolean('Books/ Manual/CDs/DVDs')
    library_remarks = fields.Text('Library Remarks')

    #Accounts Department
    previous_dues_clear = fields.Boolean('Previous Dues Cleared')
    child_benefit_exemption = fields.Boolean('Child Benefits Exemption')
    accounts_dept_remarks = fields.Text('Accounts Remarks')

    #HR Department
    notice_period = fields.Boolean('Notice Period')
    employee_card_return = fields.Boolean('Employee Card Returned')
    exit_interview_conducted = fields.Boolean('Exit Interview Conducted')
    loan_recovery = fields.Boolean('Loan Recovery')

    state = fields.Selection([('draft', 'Draft'),
                              ('Section Head', 'Section Head'),
                              ('Branch Head', 'Branch Head'),
                              ('Accounts', 'Accounts'),
                              ('HR','HR'),
                              ('done', 'Done'),
                              ('Reject', 'Reject')], default='draft',
                             string='Status', tracking=True)

    notes = fields.Text('Notes')

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('hr.employee.exit.form')
        result = super(HREmployeeExitForm, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not self.state == 'draft':
                raise UserError('You Cannot Delete The Records')
        return super(HREmployeeExitForm, self).unlink()

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
                rec.employee_father = rec.employee_id.father_name and rec.employee_id.father_name or ''
                rec.branch_id = rec.employee_id.branch_id and rec.employee_id.branch_id.id or False
                rec.city_id = rec.employee_id.city_id and rec.employee_id.city_id.id or False
                rec.cnic = rec.employee_id.cnic and rec.employee_id.cnic or ''
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.job_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False
                rec.joining_date = rec.employee_id.joining_date and rec.employee_id.joining_date or ''

    def action_section_head(self):
        for rec in self:
            rec.state = 'Section Head'

    def action_branch_head(self):
        for rec in self:
            rec.state = 'Branch Head'

    def action_accounts(self):
        for rec in self:
            rec.state = 'Accounts'

    def action_hr(self):
        for rec in self:
            rec.state = 'HR'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_reject(self):
        for rec in self:
            rec.state = 'Reject'

