# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    "name": "Birtum Contact Form",
    "version": "19.0.1.0.0",
    "category": "Customization",
    "summary": "Birtum contact form - Conditional Tabs & Filter",
    "description": """
birtum_contact_form |  TaskID: 5922409
==========================================================================
Create a Boolean field in the Contact model and add it to the form view.
When the field is True, show two additional pages in the form and add some new fields inside those pages.
Update the Contact search view by adding the new field and a filter to filter contacts based on this field.
    """,
    # Author
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    # Dependency
    "depends": ["accountant", "contacts", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "data/associate_number_sequane.xml",
        "views/activity_specialty_views.xml",
        "views/activity_type_views.xml",
        "views/company_group_views.xml",
        "views/discharge_reason_views.xml",
        "views/res_partner_views.xml",
    ],
}
