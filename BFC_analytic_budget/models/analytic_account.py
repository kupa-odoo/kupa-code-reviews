# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # override
    name = fields.Char(
        compute="_compute_name",
        store=True,
        readonly=False
    )

    project_number = fields.Many2one(
        'project.project',
        string='Project Number',
        help='Select project number from linked projects'
    )
    cost_allocation = fields.Selection(
        selection = [
            ("0", "-0 Project"),
            ("7", "-7 Early Phase"),
            ("8", "-8 Closing Postings"),
            ("9", "-9 Internal Services"),
        ],
        string="Cost Allocation"
    )
    sub_project_number = fields.Char(string="Sub Project Number", size=4)
    company_code = fields.Char(
        string="Company Code",
        related="company_id.company_code"
    )
    department = fields.Selection(
        selection = [
            ("AC", "AC"), ("FI", "FI"), ("PD", "PD"), ("LE", "LE"),
            ("DV", "DV"), ("WL", "WL"), ("GB", "GB"), ("GP", "GP"),
            ("OE", "OE"), ("VM", "VM"),
        ],
        string="Department"
    )
    cost_group_id = fields.Many2one('analytic.cost.group', string='Cost Group', help='Select the cost group from master list')
    cost_group_code = fields.Char(string='Cost Group Code', compute='_compute_cost_group_fields', store=True)
    cost_group_name = fields.Char(string='Cost Group Description', compute='_compute_cost_group_fields', store=True)
    individual_extension_code = fields.Char(string='Individual Extension Code', size=3)
    individual_extension_desc = fields.Char(string='Individual Extension Description', size=50)
    is_project_related = fields.Boolean(string="Project Related", copy=False)
    analytic_start_date = fields.Date(string="Start Date")
    analytic_end_date = fields.Date(string="End Date")

    @api.onchange('cost_allocation')
    def _onchange_cost_allocation(self):
        for rec in self:
            if not rec.cost_allocation:
                rec.sub_project_number = False
                continue
            if rec.sub_project_number and len(rec.sub_project_number) == 4:
                rec.sub_project_number = f"-{rec.cost_allocation}{rec.sub_project_number[2:]}"
            else:
                rec.sub_project_number = f"-{rec.cost_allocation}"

    @api.depends('cost_group_id')
    def _compute_cost_group_fields(self):
        for rec in self:
            rec.cost_group_code = rec.cost_group_id.code if rec.cost_group_id else False
            rec.cost_group_name = rec.cost_group_id.name_de if rec.cost_group_id else False

    @api.constrains('sub_project_number', 'cost_allocation')
    def _check_sub_project_number(self):
        for record in self.filtered(lambda r: r.sub_project_number and r.cost_allocation):
            expected_prefix = f"-{record.cost_allocation}"
            if not record.sub_project_number.startswith(expected_prefix):
                raise ValidationError(self.env._("The Sub Project Number must start with %s") % expected_prefix)
            if len(record.sub_project_number) != 4:
                raise ValidationError(self.env._("The Sub Project Number must be exactly 4 characters (e.g., -011)."))

    @api.constrains('individual_extension_code')
    def _check_extension_code(self):
        if self.individual_extension_code and not self.individual_extension_code.isalnum():
            raise ValidationError(
                self.env._("Individual Extension Code must be alphanumeric.")
            )

    @api.depends('project_number', 'sub_project_number', 'company_code', 'department', 'cost_group_code', 'cost_group_name', 'individual_extension_code', 'individual_extension_desc')
    def _compute_name(self):
        for rec in self.filtered(lambda r: r.is_project_related):
            name = ""
            if rec.project_number.project_number:
                name += f"{rec.project_number.project_number}"
            if rec.sub_project_number:
                name += f"{rec.sub_project_number}"
            if rec.company_code:
                name += f"-{rec.company_code or ''}"
            if rec.department:
                name += f"{rec.department}"
            if rec.cost_group_code:
                name += f"{rec.cost_group_code}"
            if rec.individual_extension_desc and rec.individual_extension_code:
                    name += f"{rec.individual_extension_code} {rec.individual_extension_desc}"
            elif rec.cost_group_name:
                name += f" {rec.cost_group_name}"
            rec.name = name

    def write(self, vals):
        res = super().write(vals)
        if any(key in vals for key in ("analytic_start_date", "analytic_end_date", "is_project_related")):
            BudgetLine = self.env["budget.line"]
            analytic_fields = BudgetLine._get_analytic_account_fields()
            domain = fields.Domain.OR(
                [(field, "=", self.id)]
                for field in analytic_fields
            )
            BudgetLine.search(domain)._compute_dates_from_analytic_dynamic(analytic_fields)
        return res
