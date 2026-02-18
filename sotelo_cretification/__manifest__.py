# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': "Sotelo Certification",
    'version': '19.0.1.0.0',
    'category': 'Customization',
    'summary': "Certification Integration with Project",
    'description': """
sotelo_certification |  TaskID: 5862655
==========================================================================
- Certification menu added in Project to manage project-based certifications.
- Certifications auto-load Sale Order lines and calculate totals with deductions.
- Invoices are generated from certifications using configured project products.
- Certification report can be created.
    """,

    # Author
	'author':"Odoo PS",
	'website': 'http://odoo.com',
    'license': 'LGPL-3',

    #Dependency
    'depends': ['accountant', 'project', 'sale_management'],
    'data': [
        'data/project_certification_sequence.xml',

        'security/ir.model.access.csv',

        'report/ir_actions_report.xml',
        'report/sotelo_project_certification.xml',

        'views/account_move_views.xml',
        'views/project_certification_views.xml',
        'views/project_project_views.xml',
        'views/project_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "sotelo_cretification/static/src/widget/certification_totals_widget.js",
            "sotelo_cretification/static/src/widget/certification_totals_widget.xml",
        ],
        'web.report_assets_common': [
            'sotelo_cretification/static/src/css/report.scss',
        ],
    },
}
