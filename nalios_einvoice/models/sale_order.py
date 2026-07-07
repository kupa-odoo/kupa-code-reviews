# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _group_lines_by_category(self):
        for order in self:
            order_lines = order.order_line.sorted('sequence')
            product_lines = order_lines.filtered(lambda line: not line.display_type)
            if not product_lines:
                continue
            sorted_lines = product_lines.sorted(key=lambda lines: [int(code) for code in (lines.product_id.default_code or '0').split('.') if code.isdigit()])
            grouped_by_category = {}
            for line in sorted_lines:
                category_name = line.product_id.categ_id.name or "Uncategorized"
                grouped_by_category.setdefault(category_name, []).append(line)
            sequence = 1
            section_lines = {section.name: section for section in order_lines.filtered(lambda line: line.display_type == 'line_section')}
            for category_name, category_lines in grouped_by_category.items():
                section_line = section_lines.pop(category_name, False)
                if not section_line:
                    section_line = self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'display_type': 'line_section',
                        'name': category_name,
                        'sequence': sequence,
                    })
                else:
                    section_line.sequence = sequence
                sequence += 1
                for line in category_lines:
                    line.sequence = sequence
                    sequence += 1
            remaining_lines = list(section_lines.values()) + list(order_lines - (product_lines | order_lines.filtered(lambda line: line.display_type == 'line_section')))
            for line in remaining_lines:
                line.sequence = sequence
                sequence += 1

    @api.model_create_multi
    def create(self, vals_list):
        order = super(SaleOrder, self).create(vals_list)
        order._group_lines_by_category()
        return order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self._group_lines_by_category()
        return res
