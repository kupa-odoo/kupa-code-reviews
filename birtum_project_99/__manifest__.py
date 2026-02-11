# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "BIRTUM SOLUCIONES, S.L. - project 99",
    'version': '19.0.1.0.0',
    'category': 'Customization',
    'summary': "99 Project Analytic Distribution Control",
    'description': """
birtum_project_99 |  TaskID: 5899481
==========================================================================
Ensure timesheets for 99 projects are allocated according to each employee assigned analytic account.
Enable bulk redistribution of timesheet entries through a server action when adjustments are required.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['sale_timesheet', 'accountant'],
    'data': [
        'data/server_action.xml',
        'views/account_analytic_account_views.xml',
        'views/account_analytic_plan_views.xml',
        'views/hr_department_views.xml',
        'views/project_project_views.xml',
    ],

    #Other
    'installable': True,
}
