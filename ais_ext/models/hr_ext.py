from odoo import api, fields, models
from odoo.modules.module import get_module_resource
import base64
import pdb
import logging
_logger = logging.getLogger(__name__)


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    old_id = fields.Char('Old Id')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_id = fields.Many2one('account.analytic.tag', 'Analytic Account Tag')
    to_be = fields.Boolean('To Be')

    # SARFRAZ
    @api.model
    def create(self, vals):
        dept = super(HRDepartment, self).create(vals)
        # Analytic Dimension and tag Creation
        analytic_vals = {
            'name': dept.name,
            'code': 'Department',
            'group_id': 3,
            'company_id': 1,
            'active': True,
        }
        analytic_id = self.env['account.analytic.account'].create(analytic_vals)

        tag_vals = {
            'name': dept.name,
            'analytic_dimension_id': 3,
            'company_id': 1,
            'active_analytic_distribution': True,
            'active': True,
            'analytic_distribution_ids': [(0, 0, {'account_id': analytic_id.id})],
        }

        tag_id = self.env['account.analytic.tag'].create(tag_vals)
        dept.analytic_account_id = analytic_id.id
        dept.analytic_tag_id = tag_id.id
        return dept

    #TO Account Analytic And Account Tag Entry
    @api.model
    def generate_department_dimensions(self):
        departments = self.env['hr.department'].search([('to_be', '=', True)], limit=20)
        for dept in departments:
            analytic_vals = {
                'name': dept.name,
                'code': 'Department',
                'group_id': 3,
                'company_id': 1,
                'active': True,
            }
            analytic_id = self.env['account.analytic.account'].create(analytic_vals)

            tag_vals = {
                'name': dept.name,
                'analytic_dimension_id': 3,
                'company_id': 1,
                'active_analytic_distribution': True,
                'active': True,
                'analytic_distribution_ids': [(0, 0, {'account_id': analytic_id.id})],
            }

            tag_id = self.env['account.analytic.tag'].create(tag_vals)
            dept.analytic_account_id = analytic_id.id
            dept.analytic_tag_id = tag_id.id
            dept.to_be = False
            _logger.info('Department ID= %r.......Analytic Dimension.. %r .. and Analytic Tag.. %r ..', dept.id,analytic_id.id, tag_id.id)


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'name'

    old_id = fields.Char('Old Id')
    branch_id = fields.Many2one('odooschool.campus', 'Branch', required=True)
    religion_id = fields.Char('Religion Id')
    employee_type = fields.Selection([('Managerial', 'Managerial'), ('Non-Managerial', 'Non-Managerial')],
                                     string='Employee Type')
    branch_name = fields.Char('Branch Name')
    blood_group = fields.Char('Blood Group')
    blood_group_id = fields.Char('Blood Group ID')
    alhuda_user_id = fields.Char('Alhuda Users ID')
    alhuda_address_id = fields.Char('Alhuda Address ID')
    employeeplacement_id = fields.Char('Employee Placement Id')
    joined_no = fields.Char('Joined No.')
    supervisor1 = fields.Char('Supervisor1')
    supervisor2 = fields.Char('Supervisor2')
    enrollment_status_id = fields.Many2one('hr.employment.status', 'Enrollment Status')
    phone3 = fields.Char('Phone3')
    email_2 = fields.Char('Phone3')
    to_be = fields.Boolean('To Be')

    father_name = fields.Char('Father Name')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', track_visibility='onchange')
    analytic_tag_id = fields.Many2one('account.analytic.tag', 'Analytic Account Tag', track_visibility='onchange')
    appointment_date = fields.Date('Appointment Date')
    confirmation_date = fields.Date('Confirmation Date')
    city_id = fields.Many2one('odooschool.city','City',compute='compute_branch_city',store=True)
    exit_form_id = fields.Many2one('hr.employee.exit.form','Exit Form Ref.')
    old_code = fields.Char('Old Code')
    biometric_code = fields.Char('Bio Metric Code')


    @api.model
    def create(self, vals):
        emp = super(HREmployee, self).create(vals)
        if emp.branch_id.id == 1:
            emp.code = self.env['ir.sequence'].next_by_code('hr.employee.f8')
        if emp.branch_id.id == 2:
            emp.code = self.env['ir.sequence'].next_by_code('hr.employee.h11')
        if emp.branch_id.id == 3:
            emp.code = self.env['ir.sequence'].next_by_code('hr.employee.khi')
        if emp.branch_id.id == 4:
            emp.code = self.env['ir.sequence'].next_by_code('hr.employee.pew')
        if emp.branch_id.id == 5:
            emp.code = self.env['ir.sequence'].next_by_code('hr.employee.fsd')
        if emp.branch_id.id == 6:
            emp.code = self.env['ir.sequence'].next_by_code('hr.employee.cbr')
        if emp.branch_id.id == 7:
            emp.code = self.env['ir.sequence'].next_by_code('hr.employee.hof')

        # Analytic Dimension and tag Creation
        analytic_vals = {
            'name': emp.name,
            'code': 'Employee',
            'group_id': 4,
            'company_id': 1,
            'active': True,
        }
        analytic_id = self.env['account.analytic.account'].create(analytic_vals)
        tag_vals = {
            'name': emp.name,
            'analytic_dimension_id': 4,
            'company_id': 1,
            'active_analytic_distribution': True,
            'active': True,
            'analytic_distribution_ids': [(0, 0, {'account_id': analytic_id.id})],
        }
        tag_id = self.env['account.analytic.tag'].create(tag_vals)
        emp.analytic_account_id = analytic_id.id
        emp.analytic_tag_id = tag_id.id
        return emp

    #TO Account Analytic And Account Tag Entry
    @api.model
    def generate_employee_dimensions(self):
        employees = self.env['hr.employee'].search([('to_be', '=', True)], limit=100)
        for employee in employees:
            analytic_vals = {
                'name': employee.name,
                'code': 'Employee',
                'group_id': 4,
                'company_id': 1,
                'active': True,
            }
            analytic_id = self.env['account.analytic.account'].create(analytic_vals)

            tag_vals = {
                'name': employee.name,
                'analytic_dimension_id': 4,
                'company_id': 1,
                'active_analytic_distribution': True,
                'active': True,
                'analytic_distribution_ids': [(0, 0, {'account_id': analytic_id.id})],
            }

            tag_id = self.env['account.analytic.tag'].create(tag_vals)
            employee.analytic_account_id = analytic_id.id
            employee.analytic_tag_id = tag_id.id
            employee.to_be = False
            _logger.info('Employee ID= %r.......Analytic Dimension.. %r .. and Analytic Tag.. %r ..', employee.id, analytic_id.id, tag_id.id)

            # Cron Job Used to Assign the Images to the Students

    def assign_images(self, nlimit=100):
        employees = self.search([('to_be', '=', True)], limit=nlimit)
        image_path = get_module_resource('ais_ext', 'static/src/img', 'default_image.png')
        for employee in employees:
            employee.image_1920 = base64.b64encode(open(image_path, 'rb').read())
            employee.to_be = False

    @api.depends('branch_id')
    def compute_branch_city(self):
        for rec in self:
            rec.city_id = rec.branch_id and rec.branch_id.city_id and rec.branch_id.city_id.id or False


class HRJob(models.Model):
    _inherit = 'hr.job'

    old_id = fields.Char('Old Id')
    time_in = fields.Char('TimeIn')
    time_out = fields.Char('TimeOut')
    early_departure = fields.Char('Early Departure')
    late_arrival = fields.Char('Late Arrival')
    days_skip = fields.Char('Days Skip')


class HREmploymentStatus(models.Model):
    _name = 'hr.employment.status'
    _description = 'Employment Status'

    name = fields.Char('Name')
    rank = fields.Char('Rank')
    old_id = fields.Char('Old Id')


class AISBank(models.Model):
    _name = "ais.bank"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "AIS Banks"

    name = fields.Char('Bank Name', size=128, required=True,track_visibility='onchange')
    account = fields.Char('Account', size=32,track_visibility='onchange')


class HRContract(models.Model):
    _inherit='hr.contract'
    _order = 'employee_name'

    employee_code = fields.Char('Code', compute='compute_employee_branch', store=True)
    employee_name = fields.Char(related='employee_id.name', store=True)
    branch_id = fields.Many2one('odooschool.campus',string='Campus', compute='compute_employee_branch', store=True)
    city_id = fields.Many2one('odooschool.city',string='City', compute='compute_employee_branch', store=True)
    to_be = fields.Boolean('To Be', default=False)

    @api.model
    def assign_employee_code(self):
        emps = self.env['hr.contract'].search([('to_be', '=', True)], limit=50)
        for emp in emps:
            emp.employee_code = emp.employee_id.code
            emp.name = str(emp.employee_id.code)+"-1"
            emp.to_be = False

    @api.depends('employee_id')
    def compute_employee_branch(self):
        for rec in self:
            rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
            rec.branch_id = rec.employee_id.branch_id and rec.employee_id.branch_id.id or False
            rec.city_id = rec.employee_id.branch_id and rec.employee_id.branch_id.city_id and rec.employee_id.branch_id.city_id.id or False

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            contracts = self.search_count([('employee_id', '=', self.employee_id.id)])
            contracts += 1
            self.name = str(self.employee_id.code) + '-' + str(contracts)


class HREmployeeTransfer(models.Model):
    _inherit = 'hr.employee.transfer'

    from_branch_id = fields.Many2one('odooschool.campus', 'From Branch')
    to_branch_id = fields.Many2one('odooschool.campus', 'To Branch')

    @api.model
    def create(self, values):
        result = super(HREmployeeTransfer, self).create(values)
        if result.employee_id.branch_id.id == 1:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.f8')
        if result.employee_id.branch_id.id == 2:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.h11')
        if result.employee_id.branch_id.id == 3:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.khi')
        if result.employee_id.branch_id.id == 4:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.psh')
        if result.employee_id.branch_id.id == 5:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.fsd')
        if result.employee_id.branch_id.id == 6:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.cbr')
        if result.employee_id.branch_id.id == 7:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.hof')
        return result

    def action_done(self):
        for rec in self:
            rec.state ='Done'
            rec.employee_id.branch_id = rec.to_branch_id and rec.to_branch_id.id or False
            rec.employee_id.department_id = rec.to_department_id  and rec.to_department_id.id or False
            rec.job_id = rec.to_job_id and rec.to_job_id.id or False
            contracts = self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id)])
            if contracts:
                for contract in contracts:
                    contract.branch_id = rec.to_branch_id and rec.to_branch_id.id or False
                    contract.city_id = rec.to_branch_id.city_id and rec.to_branch_id.city_id.id or False
                    contract.analytic_account_id = rec.to_branch_id.account_analytic_id and rec.to_branch_id.account_analytic_id.id or False