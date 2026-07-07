# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    client_time = fields.Float(
        "Client time",
        compute="compute_client_time",
        store=True,
        default=0.0,
    )

    @api.depends("project_id.client_percentage", "unit_amount")
    def compute_client_time(self):
        for rec in self:
            if rec.validated_status != "validated":
                rec.client_time = rec.unit_amount + (rec.unit_amount * rec.project_id.client_percentage)

    def _get_timesheet_time_day(self):
        return self._convert_hours_to_days(self.client_time)
