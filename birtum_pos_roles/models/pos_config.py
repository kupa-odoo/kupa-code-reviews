# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from odoo.fields import Domain


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sales_assistant_ids = fields.Many2many(
        'hr.employee',
        'pos_sales_assistant_employee_rel',
        string="Sales Assistants",
        help="If left empty, all employees can log in to PoS"
    )

    @api.onchange("advanced_employee_ids")
    def _onchange_advanced_employee_ids(self):
        for employee in self.advanced_employee_ids:
            if employee in self.sales_assistant_ids:
                self.sales_assistant_ids -= employee

    @api.onchange('sales_assistant_ids')
    def _onchange_basic_employee_ids(self):
        for employee in self.sales_assistant_ids:
            if employee.user_id._has_group('point_of_sale.group_pos_manager'):
                self.sales_assistant_ids -= employee
            elif employee in self.advanced_employee_ids:
                self.advanced_employee_ids -= employee

    def _employee_domain(self, user_id):
        res = super()._employee_domain(user_id)
        domain = self._check_company_domain(self.company_id)
        if len(self.sales_assistant_ids) > 0:
            domain = Domain.AND([
                domain,
                ['|', ('user_id', '=', user_id), ('id', 'in', self.sales_assistant_ids.ids + self.advanced_employee_ids.ids)]
            ])
        return domain

    def write(self, vals):
        sudo_vals = {
            field_name: value
            for field_name in ('sales_assistant_ids')
            if not self.env.su
            if (value := vals.pop(field_name, ()))
        }
        res = super().write(vals)
        if sudo_vals:
            super(PosConfig, self.sudo()).write(sudo_vals)
        return res
