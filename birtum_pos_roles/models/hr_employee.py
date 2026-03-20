# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class HrEmployee(models.Model):
    _inherit="hr.employee"

    @api.model
    def _load_pos_data_read(self, records, config):
        read_records = super()._load_pos_data_read(records, config)
        group_pos_manager = self.env.ref('point_of_sale.group_pos_manager')
        for employee in read_records:
            if employee.get('_role') != 'manager':
                employee['_role'] = 'sale_assistant'

            emp = self.browse(employee['id'])
            employee['_is_pos_manager'] = bool(group_pos_manager in emp.user_id.group_ids)
        return read_records
