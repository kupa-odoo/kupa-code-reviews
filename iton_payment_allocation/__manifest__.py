# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "ITON - Payment allocation",
    'version': '18.0.1.0.0',
    'category': 'Customization',
    'summary': "Single Payment to multiple bill or invoice allocation",
    'description': """
ITON - Payment allocation |  TaskID: 4977957
============================================
    The goal of this module is to pay multiple bill or mulitple invoice from single payment.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['account', 'sale_management'],
    'data': [
        "security/ir.model.access.csv",
        "views/account_payment_views.xml",

        "wizard/allocate_payment_views.xml",
    ],

    #Other
    'installable': True,
}
