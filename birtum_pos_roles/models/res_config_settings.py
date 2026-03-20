# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sales_assistant_ids = fields.Many2many(
        related='pos_config_id.sales_assistant_ids',
        readonly=False,
        string="Sales Assistants",
        help='If left empty, all employees can log in to PoS'
    )

    @api.onchange("pos_advanced_employee_ids")
    def _onchange_advanced_employee_ids(self):
        for employee in self.pos_advanced_employee_ids:
            if employee in self.pos_sales_assistant_ids:
                self.pos_sales_assistant_ids -= employee

    @api.onchange('pos_sales_assistant_ids')
    def _onchange_basic_employee_ids(self):
        for employee in self.pos_sales_assistant_ids:
            if employee.user_id._has_group('point_of_sale.group_pos_manager'):
                self.pos_sales_assistant_ids -= employee
            elif employee in self.pos_advanced_employee_ids:
                self.pos_advanced_employee_ids -= employee
