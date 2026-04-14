# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "Nalios - Retirement Timeline",
    'version': '18.0.1.0.0',
    'category': 'Customization',
    'summary': "Retirement Timeline",
    'description': """
Nalios - Retierement Timeline |  TaskID: 6083332
==============================================
The Goal of this module to create timeline and investment and add investment line in sale order.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['sale_crm', 'sale_project', 'website', 'documents_hr'],
    'data': [
        "data/cron.xml",

        "security/ir.model.access.csv",

        "views/crm_lead_views.xml",
        "views/crm_team_views.xml",
        "views/investment_template_portal.xml",
        "views/project_investment_report_views.xml",
        "views/project_project_views.xml",
        "views/res_config_setting_views.xml",
        "views/sale_order_views.xml",
    ]
}
