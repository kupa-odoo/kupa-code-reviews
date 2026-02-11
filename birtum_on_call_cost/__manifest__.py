# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    "name": "BIRTUM SOLUCIONES, S.L. - project & Timesheet",
    "version": "19.0.1.0.0",
    "category": "Customization",
    "summary": "add extra call employee hours",
    "description": """
birtum_on_call_cost |  TaskID: 5899477
==========================================================================
To be able to apply an extra cost to hours worked during on-call overtime.
    """,
    # Author
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    # Dependency
    "depends": ["sale_timesheet"],
    "data": [
        "views/hr_employee_views.xml",
        "views/project_task_views.xml",
    ],
    # Other
    "installable": True,
}
