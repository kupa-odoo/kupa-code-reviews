# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectSaleLineEmployeeMap(models.Model):
    _inherit = "project.sale.line.employee.map"

    extra_display_cost = fields.Monetary(
        currency_field="cost_currency_id",
        compute="_compute_extra_display_cost",
        inverse="_inverse_extra_display_cost",
        string="Extra Hourly Cost",
        groups="project.group_project_manager,hr.group_hr_user",
    )
    is_extra_cost_changed = fields.Boolean(
        "Is Extra Cost Manually Changed",
        compute="_compute_is_extra_cost_changed",
        store=True,
        export_string_translation=False,
    )
    extra_cost = fields.Monetary(
        currency_field="cost_currency_id",
        compute="_compute_extra_cost",
        store=True,
        readonly=False,
        help="This cost overrides the employee's default employee hourly wage in employee's HR Settings",
    )

    @api.depends("employee_id.extra_hourly_cost")
    def _compute_extra_cost(self):
        self.env.remove_to_compute(self._fields["is_extra_cost_changed"], self)
        for map_entry in self:
            if not map_entry.is_extra_cost_changed:
                map_entry.extra_cost = map_entry.employee_id.extra_hourly_cost or 0.0

    @api.depends("extra_cost")
    def _compute_is_extra_cost_changed(self):
        for map_entry in self:
            map_entry.is_extra_cost_changed = (
                map_entry.employee_id and map_entry.extra_cost != map_entry.employee_id.extra_hourly_cost
            )

    @api.depends_context("company")
    @api.depends("extra_cost", "employee_id.resource_calendar_id")
    def _compute_extra_display_cost(self):
        is_uom_day = self.env.ref("uom.product_uom_day") == self.env.company.timesheet_encode_uom_id
        resource_calendar_per_hours = self._get_working_hours_per_calendar(is_uom_day)

        for map_line in self:
            if is_uom_day:
                map_line.extra_display_cost = map_line.extra_cost * resource_calendar_per_hours.get(
                    map_line.employee_id.resource_calendar_id.id, 1
                )
            else:
                map_line.extra_display_cost = map_line.extra_cost

    def _inverse_extra_display_cost(self):
        is_uom_day = self.env.ref("uom.product_uom_day") == self.env.company.timesheet_encode_uom_id
        resource_calendar_per_hours = self._get_working_hours_per_calendar(is_uom_day)

        for map_line in self:
            if is_uom_day:
                map_line.extra_cost = map_line.extra_display_cost / resource_calendar_per_hours.get(
                    map_line.employee_id.resource_calendar_id.id, 1
                )
            else:
                map_line.extra_cost = map_line.extra_display_cost
