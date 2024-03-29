{
    'name': "Send SMS",
    'version': '16.0.1.1.0',
    'author': "NumDesk/Fahad",
    'category': 'Tools',
    'summary': 'You can use multiple gateway for multiple sms template to send SMS.',
    'description': 'Allows you to send SMS to the mobile no.',
    'website': "http://www.numdesk.com",
    'depends': ['base', 'web'],
    'data': [
        'view/send_sms_view.xml',
        'view/ir_actions_server_views.xml',
        'view/sms_track_view.xml',
        'view/gateway_setup_view.xml',
        'wizard/sms_compose_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
