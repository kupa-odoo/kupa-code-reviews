# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from markupsafe import Markup

from odoo import http
from odoo.http import request


class PortalSaleUpload(http.Controller):
    @http.route(["/sale/upload"], type="http", auth="user", website=True)
    def portal_sale_upload_page(self, **kwargs):
        sale_orders = request.env["sale.order"].sudo().search([
            ("partner_id", "=", request.env.user.partner_id.id),
            ("state", "=", "sale"),
            ("file_received", "=", False),
            ("followup_not_required", "=", False),
        ])
        return request.render(
            "FNT_sale_purchase_followup.portal_sale_upload_form",
            {
                "sale_orders": sale_orders,
            },
        )

    @http.route(["/sale/upload/submit"], type="http", auth="user", website=True, csrf=False)
    def portal_sale_upload_submit(self, **post):
        manual_date = post.get("manual_date")
        upload = post.get("upload_file")
        sale_id = post.get("sale_order_id")
        sale_id = int(sale_id)

        sale_order = request.env["sale.order"].sudo().browse(sale_id)
        sale_order.file_received = True

        if manual_date:
            sale_order.message_post(
                body=(
                    Markup(
                        self.env._(
                            "<b>Manual PO Update</b><br/>"
                            f"PO marked as sent manually on <b>{manual_date}</b>.<br/>"
                            f"Updated by: <b>{request.env.user.name}</b>"
                        )
                    )
                ),
                message_type="comment",
            )
            return request.render(
                "FNT_sale_purchase_followup.portal_sale_upload_success",
                {
                    "sale_order_name": sale_order.name,
                    "manual_date": manual_date,
                },
            )

        file_name = upload.filename
        request.env["ir.attachment"].sudo().create({
            "name": file_name,
            "type": "binary",
            "datas": base64.b64encode(upload.read()),
            "mimetype": upload.content_type,
            "res_model": "sale.order",
            "res_id": sale_id,
        })

        sale_order.message_post(
            body=(
                Markup(
                    self.env._(
                        "<b>PO File Uploaded</b><br/>"
                        f"File <b>{file_name}</b> uploaded by <b>{request.env.user.name}</b>."
                    )
                )
            ),
            message_type="comment",
        )

        return request.render(
            "FNT_sale_purchase_followup.portal_sale_upload_success",
            {
                "sale_order_name": sale_order.name,
            },
        )
