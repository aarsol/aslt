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
    'depends': ['base', 'account', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/invoice_ext_view.xml',
        'views/weekly_payment_view.xml',
        'views/account_journal_ext_view.xml',
        'views/customer_ext_view.xml',
        'views/templates.xml',
        'data/invoice_mail_template.xml',

    ],    
    "installable": True,
    "auto_install": False,
    'application': True,
}
