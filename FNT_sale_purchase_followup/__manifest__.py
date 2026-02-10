# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    "name": "FNT - Purchase Order Linking",
    "version": "19.0.1.0.0",
    "category": "Customization",
    "summary": "PO Follow up - linked to Sales Order",
    "description": """
FNT- Purchase Linking |  TaskID: 5456051
==========================================================================
A portal user can PO upload files to their Sales Order through the portal,
and a reminder can be sent if they do not upload the PO file within a certain time period
""",
    # Author
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "license": "LGPL-3",
    # Dependency
    "depends": ["sale_management", "website", "contacts"],
    "data": [
        "data/website_menu.xml",
        "data/cron_followup.xml",
        "views/portal_sale_upload_views.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
        "views/sale_portal_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "FNT_sale_purchase_followup/static/src/widget/po_overdue_widget.js",
            "FNT_sale_purchase_followup/static/src/widget/po_overdue_widget.xml",
        ],
        "web.assets_frontend": [
            "FNT_sale_purchase_followup/static/src/js/portal_sale_upload.js",
        ],
    },
    # Other
    "installable": True,
}
