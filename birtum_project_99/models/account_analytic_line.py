# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._update_is_department_analytic_line_field()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if 'employee_id' in vals or 'project_id' in vals:
            self._update_is_department_analytic_line_field()
        return res

    def _get_is_department_analytic_field(self, record):
        """Return (field_name, account) for the first analytic field linked to a department plan."""
        if not record:
            return False, False
        department_plan = self.env['account.analytic.plan'].search([('is_department', '=', True)], limit=1)
        if not department_plan:
            return False, False
        field_record = department_plan._find_plan_column(model=record._name)
        if not field_record:
            return False, False
        return field_record.name, record[field_record.name]

    def _update_is_department_analytic_line_field(self):
        """Update analytic account line with their relevant department analytic accounts."""
        for line in self:
            project = line.project_id
            employee_dept_acc = line.employee_id.department_id.analytic_account if line.employee_id.department_id else None
            field_name, project_acc = self._get_is_department_analytic_field(project)
            if not field_name:
                continue
            if project_acc and project_acc.is_99 and employee_dept_acc:
                new_value = employee_dept_acc
            else:
                new_value = project[field_name]

            if line[field_name] != new_value:
                line[field_name] = new_value

    def action_update_timesheet_analytic_account(self):
        self._update_is_department_analytic_line_field()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
