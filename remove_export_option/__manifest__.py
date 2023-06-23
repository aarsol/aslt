{
    'name': 'Remove Export Option',
    'description': 'Remove the Export option from the More menu...',
    'version': '16.0.1.1.0',
    'summary': 'A useful module which allows removal of export option easily using the access rights and permissions from the user Settings',
    'license': 'GPL-3',
    'author': 'NumDesk/Fahad',
    'website': 'https://www.numdesk.com',
    'category': 'Web',
    'description': """

Remove the 'Export' option from the 'More' menu using hide group...
in the list view except for the admin user

""",
    'depends': ['web'],
    "assets": {
        "web.assets_backend": [
            "remove_export_option/static/src/js/remove_export_option.js"
        ],
    },
    'data': [
        'security/export_visible_security.xml',
        # 'view/disable_export_view.xml',
    ],
    'auto_install': False,
}
