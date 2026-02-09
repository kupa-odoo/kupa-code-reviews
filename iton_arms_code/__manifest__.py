# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "Iton - Arms Code",
    'version': '18.0.1.0.0',
    'category': 'Customization',
    'summary': "Differentiate products using an arms code",
    'description': """
ITON Arms Code  |  TaskID: 5715254
==================================
Add a new field to the Arms Code, include it in the search view, add length, width, and height fields, and calculate the volume based on these dimensions
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['mrp', 'purchase', 'sale_management', 'stock'],
    'data': [
        'views/mrp_production_views.xml',
        'views/product_product_views.xml',
        'views/product_strategy_views.xml',
        'views/product_template_views.xml',
        'views/stock_lot_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_move_views.xml',
        'views/stock_orderpoint_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_quant_views.xml',
        'views/stock_scrap_views.xml',
        'views/stock_valuation_layer.xml'
    ]
}
