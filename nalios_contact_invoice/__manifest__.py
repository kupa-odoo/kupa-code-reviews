# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "Nalios - Contacts & Invoice",
    'version': '18.0.1.0.0',
    'category': 'Customization',
    'summary': "Contacts & Invoice",
    'description': """
Nalios - Contacts & Invoice |  TaskID: 5974145
==============================================
The Goal of this module improve the dousseramonage_custos module and extend some functionality.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['dousseramonage_custos', 'nalios_sale_invoice'],
    'data': [
        'views/contact_address_views.xml',
        'views/report_invoice.xml',
        'views/standard_work_views.xml',
        'views/installations_view.xml'
    ]
}
