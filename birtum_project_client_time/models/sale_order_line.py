# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, models
from odoo.fields import Domain


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        super()._get_delivered_quantity_by_analytic(additional_domain)
        result = defaultdict(float)
        if not self:
            return result
        domain = Domain.AND([[("so_line", "in", self.ids)], additional_domain])
        data = self.env["account.analytic.line"]._read_group(
            domain,
            ["product_uom_id", "so_line"],
            ["client_time:sum", "move_line_id:count_distinct", "__count"],
        )
        for uom, so_line, client_time_sum, move_line_id_count_distinct, count in data:
            if not uom:
                continue
            qty = client_time_sum / count if move_line_id_count_distinct == 1 and count > 1 else client_time_sum
            qty = uom._compute_quantity(qty, so_line.product_uom_id, rounding_method="HALF-UP")
            result[so_line.id] += qty
        return result

    @api.depends("analytic_line_ids.project_id", "project_id.pricing_type", "task_id.project_id.client_percentage")
    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()
