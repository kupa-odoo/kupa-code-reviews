# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    extra_hourly_cost = fields.Monetary(
        "Extra Hourly Cost", currency_field="currency_id", groups="hr.group_hr_user", default=0.0, tracking=True
    )
