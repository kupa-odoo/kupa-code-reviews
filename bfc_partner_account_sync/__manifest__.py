# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # Information
    "name": "BFC Partner Account Sync",
    "version": "19.0.1.0.0",
    "category": "Custom Development",
    "summary": "Sync partner accounts configuration to child companies.",
    "description": """
        BFC Product Account Sync | Task : 6048272
        ===============================================
        This module propagates the master company's partner
        account configuration to selected child companies.
    """,
    # Author
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    # Dependency
    "depends": ["bfc_master_company_coa_sync", 'contacts', 'purchase', 'sale_management'],
    "data": [
        'data/ir_actions_server.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml'
    ],
}
