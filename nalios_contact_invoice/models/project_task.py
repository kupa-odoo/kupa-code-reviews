# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProjectTask(models.Model):
    _inherit="project.task"

    def _fsm_create_sale_order_line_for_order(self, order):
        self.ensure_one()
        existing_lines = order.order_line
        super()._fsm_create_sale_order_line_for_order(order)
        new_sections = (
            order.order_line - existing_lines
        ).filtered(lambda l: l.display_type == 'line_section')
        if installations := self.fsm_intervention_ids.installation_id:
            for section, inst in zip(new_sections, installations):
                section.name = (
                    f"Installation n°{inst.number_installation or ''}: "
                    f"{inst.titles.name or ''}"
                    f"{f' - {inst.access_specifications}' if inst.access_specifications else ''}"
                )
