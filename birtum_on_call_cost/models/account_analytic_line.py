# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_on_call = fields.Boolean("Is On Call", default=False)

    def _hourly_cost(self):
        res = super()._hourly_cost()
        if self.is_on_call:
            mapping_entry = self._get_employee_mapping_entry()
            if mapping_entry:
                return res + mapping_entry.extra_cost or 0.0
        return res

    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)
        if "is_on_call" in values and not any(k in values for k in ("unit_amount", "employee_id", "account_id")):
            sudo_self = self.sudo()
            for timesheet in sudo_self:
                if not timesheet.account_id.active:
                    project_plan, _other_plans = self.env["account.analytic.plan"]._get_all_plans()
                    raise ValidationError(
                        _(
                            "Timesheets must be created with at least an active analytic account defined in the plan '%(plan_name)s'.",
                            plan_name=project_plan.name,
                        )
                    )
                accounts = timesheet._get_analytic_accounts()
                companies = (
                    timesheet.company_id
                    | accounts.company_id
                    | timesheet.task_id.company_id
                    | timesheet.project_id.company_id
                )
                if len(companies) > 1:
                    raise ValidationError(
                        _(
                            "The project, the task and the analytic accounts of the timesheet must belong to the same company."
                        )
                    )
                cost = timesheet._hourly_cost()
                amount = -timesheet.unit_amount * cost
                amount_converted = timesheet.employee_id.currency_id._convert(
                    amount, timesheet.account_id.currency_id or timesheet.currency_id, self.env.company, timesheet.date
                )
                result[timesheet.id].update({
                    "amount": amount_converted,
                })
        return result
