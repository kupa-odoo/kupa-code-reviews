# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "BFC - Journal Syncronization",
    'version': '19.0.1.0.0',
    'category': 'Customization',
    'summary': "Journal syncronization from main company",
    'description': """
BFC - Journal Syncronization| TaskID:6048257
=============================================
The goal of this module is to syncronization of all companies Journal with main company.
""",

    # Author
    'author': 'Odoo PS',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',

    # Dependency
    'depends': ['account_debit_note', 'bfc_master_company_coa_sync'],

    'data': [
        'data/ir_action_server.xml',
        'views/res_company_views.xml',
        'views/account_journal_views.xml'
    ],
    # # Other
    # 'installable': True,
}
