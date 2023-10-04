# -*- coding: utf-8 -*-
# Copyright 2020 - Today AmazeWorks Technologies.
# Part of AmazeWorks Technologies. See LICENSE file for full copyright and licensing details.
{
    'name': 'Profitibilty Calculation by Analytic Account',
    'description': """
        - Set auto Analytic Number on Customer Invoice
        - Calculation of Cost Percentage
        - Add Salesper and stages
    """,
    'summary': """
         Auto Analytic Number on Customer Invoice
    """,
    'version': '1.1',
    'author': 'Ansa Saeed., M.Umais., Usman F.',
    'category': 'Account',
    'company': 'AmazeWorks Technologies.',
    'maintainer': 'AmazeWorks Technologies.',
    'website': "https://www.odoospecialist.com",
    'depends': [
                'base',
                'account',
                'analytic',
               ],
    'data': [
        
        # Views
        'views/account_analytic_account_tree_view.xml'
        
    ],
    
    # 'images': ['static/description/banner.gif'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'price': 980.00,
    'currency': 'USD',
    'license': 'OPL-1',
}
