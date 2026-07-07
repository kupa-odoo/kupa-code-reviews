# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class BudgetLine(models.Model):
    _inherit = 'budget.line'

    project_budget = fields.Monetary(string="Basebudget", help="initial budget")
    expected_additional_value = fields.Monetary(string="Expected Additional Value")
    forecast = fields.Monetary(string="Available", compute="_compute_forecast", help="Available before expected supplementary budget: Calculation = (current) budget - committed")
    cost_allocation = fields.Selection(
        [
            ("0", "-0 Project"),
            ("7", "-7 Early Phase"),
            ("8", "-8 Closing Postings"),
            ("9", "-9 Internal Services"),
        ],
        string="Cost Allocation",
    )
    analytic_start_date = fields.Date(readonly=True)
    analytic_end_date = fields.Date(readonly=True)

    # Added from module ece_analytic_budget_stored
    achieved_amount_stored = fields.Monetary(
        string="Achieved (Stored)",
        help="Manual historical actual cost amount. "
        "Use when past invoices are not available. "
        "This amount is added to the current actual cost calculation "
        "to include costs from the past.",
    )

    @api.onchange("account_id")
    def _onchange_analytic_account_cost_allocation(self):
        for line in self:
            aa = line.account_id
            line.cost_allocation = aa.cost_allocation if aa else False

    def _compute_dates_from_analytic_dynamic(self, analytic_fields):
        if self.env.context.get("skip_analytic_date_compute"):
            return
        if not analytic_fields:
            analytic_fields = self._get_analytic_account_fields()
        for line in self:
            account = False
            for field in analytic_fields:
                if (line[field] and line[field].is_project_related and line[field].analytic_start_date and line[field].analytic_end_date):
                    account = line[field]
                    break
            line.with_context(skip_analytic_date_compute=True).write({
                "analytic_start_date": account.analytic_start_date if account else False,
                "analytic_end_date": account.analytic_end_date if account else False,
            })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._compute_dates_from_analytic_dynamic(analytic_fields=None)
        return records

    def write(self, vals):
        res = super().write(vals)
        analytic_fields = self._get_analytic_account_fields()
        if any(field in vals for field in analytic_fields) and not self.env.context.get("skip_analytic_date_compute"):
            self._compute_dates_from_analytic_dynamic(analytic_fields)
        return res

    @api.model
    def _get_analytic_account_fields(self):
        analytic_fields = []
        for name, field in self._fields.items():
            if field.type == "many2one" and field.comodel_name == "account.analytic.account" and name not in {"account_id", "auto_account_id"}:
                analytic_fields.append(name)
        return analytic_fields

    def _compute_forecast(self):
        grouped = {
            line: forecast
            for line, forecast in self.env['budget.report'].with_context(budget_report_budget_line_ids=self.ids)._read_group(
                domain=[('budget_line_id', 'in', self.ids)],
                groupby=['budget_line_id'],
                aggregates=['forecast:sum'],
            )
        }
        for line in self:
            line.forecast = grouped.get(line, 0.0)
