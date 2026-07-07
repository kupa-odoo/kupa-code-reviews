# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    "name": "BIRTUM SOLUCIONES, S.L. - project & Timesheet",
    "version": "19.0.1.0.0",
    "category": "Customization",
    "summary": "add extra client hours in the project and timesheet",
    "description": """
BIRTUM SOLUCIONES, S.L. |  TaskID: 5899478
==========================================================================
Calculate a new field “Client Time” based on the client percentage defined on the project.
Add a new button on the Project Dashboard to display the Client Timesheet.
Add the Client Time field to the Portal and update the relevant portal views to show this information.
Update a smart button on the Sales Order to show client timesheet.
Update the delivery information on the Sales Order Line based on the calculated client time.
    """,
    # Author
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    # Dependency
    "depends": ["sale_timesheet_enterprise", "website_timesheet"],
    "data": [
        "views/hr_timesheet_views.xml",
        "views/project_project_views.xml",
        "views/project_portal_project_task_template.xml",
        "views/project_task_views.xml",
        "views/project_task_sharing_views.xml",
        "views/portal_timesheet_templates.xml",
        "views/sale_order_views.xml",
        "report/report_timesheet_templates.xml",
    ],
    # Other
    "installable": True,
}
