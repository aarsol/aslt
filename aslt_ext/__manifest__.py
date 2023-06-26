{
    'name': "ASLT",
    'summary': """
        Extension for ASLT Project""",

    'description': """
        Extension for ASLT Project
    """,

    'author': "NumDesk/Fahad",
    'website': "http://www.numdesk.com",
    'category': 'Accounts',
    'sequence': -100,
    'version': '16.0.1.1.0',
    'depends': ['base', 'account', 'sale', 'sale_management', 'branch', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/aslt_security.xml',
        'views/invoice_ext_view.xml',
        # 'views/invoice_ext_template.xml',
        'views/weekly_payment_view.xml',
        'views/account_journal_ext_view.xml',
        'views/customer_ext_view.xml',
        # 'views/templates.xml',
        # 'views/sale_portal_templates.xml',
        'views/res_partner_view.xml',

        'wizard/merge_customer_wiz.xml',
        'wizard/invoice_rate_wiz.xml',
        'wizard/invoice_wise_profit_wiz.xml',
        'wizard/account_tax_report_view.xml',

        'reports/reports.xml',
        'reports/sale_report_templates.xml',
        'reports/invoice_report_templates.xml',
        'reports/invoice_wise_report.xml'

        # 'data/invoice_mail_template.xml',

    ],
    "assets": {
        "web.assets_frontend": [
            "aslt_ext/static/src/js/name_and_signature.js",
            "aslt_ext/static/src/js/portal_signature.js"
        ]
        # "web.assets_frontend": [
        #     "aslt_ext/static/src/js/portal_signature.js"
        # ]
    },
    "installable": True,
    "auto_install": False,
    'application': True,
}
