# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    is_department = fields.Boolean("Is Department")

    @api.constrains('is_department')
    def _check_unique_department_plan(self):
        for record in self:
            if record.is_department:
                existing = self.search([('is_department', '=', True), ('id', '!=', record.id)], limit=1)
                if existing:
                    raise UserError(self.env._(
                        "Only one Analytic Plan can be marked as 'Is Department'.\n\n"
                        "Current Department Plan: %s"
                    ) % existing.display_name)
