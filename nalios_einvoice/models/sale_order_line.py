# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_section_quantities(self):
        self.ensure_one()
        section_lines = self._get_section_lines()
        if not section_lines:
            return 0, None
        uom_ids = section_lines.mapped('product_uom_id')
        if len(uom_ids) == 1:
            total_qty = sum(section_lines.mapped('product_uom_qty'))
            return total_qty, uom_ids[0]
        else:
            return 0, None
