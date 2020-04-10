# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class GenerateEmployeeExitForm(models.TransientModel):
    _name = "generate.employee.exit.form"
    _description = 'This Wizard Will Generate the Employee Exit Form'

    @api.model
    def _get_employee(self):
        if self._context.get('active_model', False) == 'hr.employee' and self._context.get('active_id', False):
            return self.env['hr.employee'].browse(self._context.get('active_id', False))

    employee_id = fields.Many2one('hr.employee','Employee Name',default=_get_employee, required=True)
    date = fields.Date('Date', default=fields.Date.today())

    def generate_exit_form_funct(self):
        for rec in self:
            if rec.employee_id:
                entry_exit = self.env['hr.employee.exit.form'].search([('employee_id','=',rec.employee_id.id)])
                if entry_exit:
                    raise UserWarning('This Employee Already Exists in the Exit Form')
                else:
                    exit_vals = {
                        'employee_id' : rec.employee_id and rec.employee_id.id or False,
                        'employee_code' : rec.employee_id.code and rec.employee_id.code or '',
                        'employee_father' : rec.employee_id.father_name and rec.employee_id.father_name or '',
                        'cnic' : rec.employee_id.cnic and rec.employee_id.cnic or '',
                        'branch_id' : rec.employee_id.branch_id and rec.employee_id.branch_id.id or False,
                        'city_id' : rec.employee_id.city_id and rec.employee_id.city_id.id or False,
                        'department_id' : rec.employee_id.department_id and rec.employee_id.department_id.id or False,
                        'job_id' : rec.employee_id.job_id and rec.employee_id.job_id.id or False,
                        'joining_date' : rec.employee_id.joining_date and rec.employee_id.joining_date or '',
                        'leaving_date' : rec.date,
                    }
                    new_rec = self.env['hr.employee.exit.form'].create(exit_vals)
                    rec.employee_id.exit_form_id = new_rec.id
                    contracts = self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id),('state','=','open')])
                    if contracts:
                        contracts.write({'state':'close','date_end':rec.date})
                    rec.employee_id.active = False
