{
	'name': 'AIS Extensions',
	'version': '13.0.1.0.1',
	'category': 'OdooCMS',
    'sequence': 6,
	'license': 'AGPL-3',
	'description': "This module adds the extensions for Schools Core Functionality.",
	'author': 'Farooq',
	'website': 'http://www.aarsolerp.com/',
	'depends': ['base', 'mail','hr','website','odooschool'],
	
	'data': [
		'security/ir.model.access.csv',
		'data/data.xml',

		'views/hr_ext_view.xml',
		'views/hr_contract_ext_view.xml',
		# 'views/hr_payslip_ext_view.xml',
		'views/ais_bank_view.xml',
		'views/hr_staff_advance_view.xml',
		'views/loan_view.xml',
		'views/hr_employee_exit_form_view.xml',

		'wizard/reports/employee_excel_rep_view.xml',
		'wizard/reports/no_contract_employee_rep_view.xml',
		'wizard/reports/salary_report_view.xml',

		'wizard/config/generate_employee_exit_form_view.xml',
		'wizard/config/employee_transfer_wiz_view.xml',

		'menu/menu.xml',
		
	],	
	'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}


