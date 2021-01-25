# -*- coding: utf-8 -*-
{
    'name': "ASLT",
    'summary': """
        Extension for ASLT Project""",

    'description': """
        Extension for ASLT Project
    """,

    'author': "Numan Ali",
    'website': "http://www.aarsol.com",
    'category': 'Accounts',
    'version': '0.1',
    'sequence': 2,
    'depends': ['base', 'account', 'sale', 'sale_management', 'branch'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/aslt_security.xml',
        'views/invoice_ext_view.xml',
        'views/invoice_ext_template.xml',
        'views/weekly_payment_view.xml',
        'views/account_journal_ext_view.xml',
        'views/customer_ext_view.xml',
        'views/templates.xml',
        'views/sale_portal_templates.xml',
        'views/res_partner_view.xml',

        'wizard/merge_customer_wiz.xml',
        'wizard/invoice_rate_wiz.xml',
        'wizard/invoice_wise_profit_wiz.xml',
        'wizard/account_tax_report_view.xml',

        'reports/reports.xml',
        'reports/sale_report_templates.xml',
        'reports/invoice_wise_report.xml',

        'data/invoice_mail_template.xml',

    ],
    "installable": True,
    "auto_install": False,
    'application': True,
}
