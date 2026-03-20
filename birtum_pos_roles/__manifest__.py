# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "birtum- Pos Role",
    'version': '19.0.1.0.0',
    'category': 'Customization',
    'summary': "Birtum POS Role - sale assistant",
    'description': """
birtum_pos_roles |  TaskID: 6041405
==========================================================================
The main goal of this module is add a new point of sale role called Sales Assistant with specific access permissions.
Additionally, the standard Basic and Minimal roles have been removed. and do some modfication in Advanced role.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['pos_discount', 'pos_hr', 'pos_restaurant'],
    'data': [
        'views/pos_config.xml',
        'views/res_config_settings_views.xml'
    ],

    'assets':{
        'point_of_sale._assets_pos': [
            'birtum_pos_roles/static/src/**/*'
        ]
    }
}
