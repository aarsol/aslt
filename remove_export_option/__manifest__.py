
{
    'name': 'Remove Export Option',
    'description': 'Remove the Export option from the More menu...',
    'version': '1.1',
    'summary': 'A useful module which allows removal of export option easily using the access rights and permissions from the user Settings',
    'license': 'OPL-1',
    'author': 'Farooq',
    'website': 'https://www.aarsol.com',
    'category': 'Web',
    'description': """

Remove the 'Export' option from the 'More' menu using hide group...
in the list view except for the admin user

""",
    'depends': ['web'],
    'data': [
        'security/export_visible_security.xml',
        'view/disable_export_view.xml',
    ],
    'auto_install': False,
}
