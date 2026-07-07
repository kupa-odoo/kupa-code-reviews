# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "Business First Consulting GmbH - Analytic Budget",
    'version': '19.0.1.0.0',
    'category': 'Customization',
    'summary': "Expansion of the analytic budget view and related functions",
    'description': """
Business First Consulting GmbH  |  TaskID: 5402718, 5436007
==========================================================================
Add a four field in budget.line model with some constraint model and show field in list and form views.
Add a three field in budget.report model and in all views(pivot, graph)
Compute the name of analytic account based on some custom fields.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['account_budget_purchase', 'contacts', 'analytic', 'project', 'company_selector' ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_analytic_account_views.xml',
        'views/analytic_cost_group_views.xml',
        'views/budget_analytic_views.xml',
        'views/budget_line_views.xml',
        'views/budget_report_views.xml',
        'views/project_project_views.xml',
    ]
}
