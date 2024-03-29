{
    'name': 'Multiple Branch(Unit) Operation Setup for All Applications Odoo/OpenERP',
    'version': '16.0.1.1.0',
    'category': 'Sales',
    'summary': 'Multiple Branch/Unit Operation on Sales,Purchases,Accounting/Invoicing,Voucher,Paymemt,POS, Accounting Reports for single company',
    "description": """
    odoo Multiple Unit operation management for single company Mutiple Branch management for single company
    odoo multiple operation for single company. branching company in odoo multiple store multiple company in odoo
    odoo Branch for POS Branch for Sales Branch for Purchase Branch for all Branch for Accounting Branch for invoicing Branch for Payment order Branch for point of sales Branch for voucher 
    odoo Unit for POS Unit for Sales Unit for Purchase Unit for all Unit for Accounting Unit for invoicing Unit for Payment order
    odoo Unit for point of sales Unit for voucher Unit for All Accounting reports Unit Accounting filter

  odoo Unit Operation for POS Unit Operation for Sales Unit operation for Purchase Unit operation for all Unit operation for Accounting 
  odoo Unit Operation for invoicing Unit operation for Payment order Unit operation for point of sales Unit operation for voucher Unit operation for All Accounting reports
  odoo Unit operation Accounting filter Branch Operation for POS Branch Operation for Sales 
  odoo Branch operation for Purchase Branch operation for all Branch operation for Accounting Branch Operation for invoicing
  odoo Branch operation for Payment order Branch operation for point of sales Branch operation for voucher Branch operation for All Accounting reports Branch operation Accounting filter.
  odoo branch helpdesk and support branch support and helpdesk
  odoo helpdesk branch helpdesk unit helpdek multiple unit helpdesk operation unit
  odoo branch crm odoo crm branch crm operating unit crm unit operation management crm multiple unit operating unit crm
  odoo branch Subscription branch contract Subscription branch management
  odoo contract branch management operating unit Subscription operating unit contract
  odoo Subscription unit management contract unit management Subscription operating unit management
  odoo contract operating unit management operating unit for company multi branch management
  odoo multi branch application multi operation unit application multi branch odoo multi branch
  odoo all in one multi branch application multi branch unit operation multi unit operation branch management
  odoo multi branches management application multi operation mangement operating Unit for POS operating Unit for Sales
  odoo operating Units for Purchase operating Unit for all operating Unit for Accounting operating Unit for invoicing
  odoo operating Unit for Payment order operating Unit for point of sales operating Unit for voucher operating Unit for All Accounting reports operating Unit Accounting filter.

odoo operating-Unit Operation for POS operating-Unit Operation for Sales operating-Unit operation for Purchase operating-Unit operation for all 
odoo operating-Unit operation for Accounting operating-Unit Operation for invoicing operating-Unit operation for Payment order operating-Unit operation for point of sales 
odoo operating-Unit operation for voucher operating-Unit operation for All Accounting reports operating-Unit operation Accounting filter.
odoo multi branches management odoo branches management odoo multiple branches management on odoo branchs management
odoo many branches for single company odoo
    """,
    'author': 'NumDesk/Fahad',
    'website': 'http://www.numdesk.com',
    'sequence': 3,
    'depends': ['base', 'sale_management', 'purchase', 'account', 'stock'],
    'data': [
        'security/branch_security.xml',
        'security/ir.model.access.csv',
        'views/res_branch_view.xml',
        'views/inherited_res_users.xml',
        'views/inherited_sale_order.xml',

        'views/inherited_account_invoice.xml',
        'views/inherited_purchase_order.xml',

        'views/inherited_account_bank_statement.xml',
        # 'wizard/inherited_account_payment.xml',

        'views/inherited_product.xml',
        'views/inherited_partner.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
