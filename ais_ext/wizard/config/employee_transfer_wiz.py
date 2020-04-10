from odoo import fields, models, api, _
from odoo.exceptions import ValidationError,UserError
import pdb


class HREmployeeTransferWiz(models.TransientModel):
    _name = 'hr.employee.transfer.wiz'
    _description = 'Employee Transfer Wiz'

    @api.model
    def _get_employees(self):
        if self._context.get('active_model', False) == 'hr.employee' and self._context.get('active_ids', False):
            return self.env['hr.employee'].browse(self._context.get('active_ids', False))

    employee_ids = fields.Many2many('hr.employee','transfer_wiz_employee_rel','transfer_wiz_id','emp_id','Employee(s)', default=_get_employees)
    to_department_id = fields.Many2one('hr.department', 'To Department')
    to_job_id = fields.Many2one('hr.job', 'To Designation')
    to_branch_id = fields.Many2one('odooschool.campus', 'To Branch')
    transfer_date = fields.Date('Transfer Date', default=fields.Date.today())

    def employee_transfer_fuct(self):
        users = self.env['res.groups'].search([('name', '=', 'MIS Manager')]).users
        if not self.env.user.id in users.ids:
            raise UserError('You Cannot Do this Action, Please Contact the System Administrator.')
        else:
            for rec in self:
                for employee_id in rec.employee_ids:
                    vals = {
                        'employee_id': employee_id and employee_id.id or False,
                        'from_branch_id' : employee_id.branch_id and employee_id.branch_id.id or False,
                        'to_branch_id':rec.to_branch_id and rec.to_branch_id.id or False,
                        'from_department_id': employee_id.department_id and employee_id.department_id.id or False,
                        'to_department_id': rec.to_department_id and rec.to_department_id.id or False,
                        'from_job_id': employee_id.job_id and employee_id.job_id.id or False,
                        'to_job_id': rec.to_job_id and rec.to_job_id.id or False,
                        'transfer_date': rec.transfer_date,
                        'state': 'Done',
                        'remarks' : '',
                    }
                    result = self.env['hr.employee.transfer'].create(vals)
                    if not result.name:
                        if employee_id.branch_id.id == 1:
                            result.name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.f8')
                        if employee_id.branch_id.id == 2:
                            name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.h11')
                        if employee_id.branch_id.id == 3:
                            name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.khi')
                        if result.employee_id.branch_id.id == 4:
                            name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.psh')
                        if result.employee_id.branch_id.id == 5:
                            name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.fsd')
                        if result.employee_id.branch_id.id == 6:
                            name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.cbr')
                        if result.employee_id.branch_id.id == 7:
                            name = self.env['ir.sequence'].next_by_code('hr.employee.transfer.hof')

                    employee_id.branch_id = rec.to_branch_id and rec.to_branch_id.id or False
                    employee_id.department_id = rec.to_department_id and rec.to_department_id.id or False
                    employee_id.job_id = rec.to_job_id and rec.to_job_id.id or False

                    contracts = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)])
                    if contracts:
                        for contract in contracts:
                            contract.branch_id = rec.to_branch_id and rec.to_branch_id.id or False
                            contract.city_id = rec.to_branch_id.city_id and rec.to_branch_id.city_id.id or False
                            contract.analytic_account_id = rec.to_branch_id.account_analytic_id and rec.to_branch_id.account_analytic_id.id or False
