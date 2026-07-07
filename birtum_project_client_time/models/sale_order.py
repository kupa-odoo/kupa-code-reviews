# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    timesheet_client_total_duration = fields.Integer(
        "Timesheet Client Total Duration",
        compute="compute_timesheet_client_total_duration",
        compute_sudo=True,
        groups="hr_timesheet.group_hr_timesheet_user",
        export_string_translation=False,
    )

    @api.depends("company_id.project_time_mode_id", "company_id.timesheet_encode_uom_id", "order_line.timesheet_ids")
    def compute_timesheet_client_total_duration(self):
        group_data = self.env["account.analytic.line"]._read_group(
            [("order_id", "in", self.ids), ("project_id", "!=", False)],
            ["order_id"],
            ["client_time:sum"],
        )
        timesheet_client_time_dict = defaultdict(float)
        timesheet_client_time_dict.update({order.id: client_time for order, client_time in group_data})
        for sale_order in self:
            total_time = sale_order.company_id.project_time_mode_id._compute_quantity(
                timesheet_client_time_dict[sale_order.id],
                sale_order.timesheet_encode_uom_id,
                rounding_method="HALF-UP",
            )
            sale_order.timesheet_client_total_duration = round(total_time)
