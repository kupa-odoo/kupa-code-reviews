# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "NALIOS SARL - Blue Kira Invoice",
    'version': '19.0.1.0.0',
    'category': 'Customization',
    'summary': "Adding specific fields and modifying eInvoice format and change in the pdf report",
    'description': """
NALIOS SARL - swiss |  TaskID: 5123674
==========================================================================
Add custom fields to partners and products, create a customer type and product code mapping,
customize the eInvoice format, modify delivery slip and quotation PDFs with additional fields and sorting.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['base', 'stock', 'sale_management', 'account', 'account_edi_ubl_cii', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/cii_22_templates.xml',
        'report/ir_actions_report_templates.xml',
        'report/report_deliverslip.xml',
        'views/partner_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/stock_picking_views.xml',
    ],

    #Other
    'installable': True,
}
