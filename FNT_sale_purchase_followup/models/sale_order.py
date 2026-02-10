# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from markupsafe import Markup

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    file_received = fields.Boolean(
        string="File Received",
        tracking=True,
    )
    followup_not_required = fields.Boolean(
        string="Followup Not Required",
        tracking=True,
    )
    next_reminder_date = fields.Date(
        string="Next Reminder Date",
        tracking=True,
    )
    is_po_overdue = fields.Boolean(string="Is PO Overdue")

    @api.model
    def cron_followup_sales_orders(self):
        """
        Automatically sends follow-up notifications for confirmed sales orders
        where the required Purchase Order has not been received.
        """
        today = fields.Date.context_today(self)

        orders = self.env["sale.order"].search([
            ("state", "=", "sale"),
            ("file_received", "=", False),
            ("followup_not_required", "=", False),
            ("next_reminder_date", "=", today),
        ])

        for order in orders:
            interval = order.company_id.so_followup_interval
            partner_message = Markup(
                self.env._(f"""
                    <b>Automatic Follow-Up</b><br/>
                    <b>Sales Order:</b> {order.name}<br/>
                    The required PO has not been received yet.<br/>
                    Next follow-up will be scheduled in <b>{interval} days</b>.
                """)
            )
            if order.is_po_overdue and order.user_id:
                salesperson_message = Markup(
                    self.env._(f"""
                        <b>PO Overdue - Action Required</b><br/>
                        <b>Sales Order:</b> {order.name}<br/>
                        The Purchase Order (PO) has not been received within the configured follow-up period.<br/>
                        Please follow up with the customer to obtain the required PO.<br/>
                    """)
                )
                order.message_post(
                    body=salesperson_message,
                    partner_ids=[order.user_id.partner_id.id],
                    subtype_xmlid="mail.mt_note",
                )

            order.message_post(
                body=partner_message,
                subject=f"Sales Order Follow-Up - {order.name}",
                partner_ids=[order.partner_id.id],
                message_type="notification",
            )
            order.is_po_overdue = True
            order.next_reminder_date = today + timedelta(days=interval)

    def action_confirm(self):
        res = super().action_confirm()
        today = fields.Date.context_today(self)
        for rec in self:
            rec.write({"next_reminder_date": today + timedelta(days=rec.company_id.so_followup_interval)})
        return res
