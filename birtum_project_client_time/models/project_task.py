# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    subtask_client_effective_hours = fields.Float(
        "Client Time Spent on Sub-tasks",
        compute="compute_subtask_client_effective_hours",
        recursive=True,
        store=True,
        help="Time spent on the sub-tasks (and their own sub-tasks) of this task.",
    )
    total_client_hours_spent = fields.Float(
        "Total Client Time Spent",
        compute="compute_client_total_hours_spent",
        store=True,
        help="Time spent on this task and its sub-tasks (and their own sub-tasks).",
    )
    portal_effective_client_hours = fields.Float(
        "Portal Effective Client TIme",
        compute="compute_project_sharing_client_timesheets",
        help="Time spent on this task, excluding its sub-tasks.",
    )
    portal_total_client_hours_spent = fields.Float(
        compute="compute_project_sharing_client_timesheets",
        help="Time spent on this task, including its sub-tasks.",
        export_string_translation=False,
    )
    portal_subtask_client_effective_hours = fields.Float(
        compute="compute_project_sharing_client_timesheets",
        help="Time spent on the sub-tasks (and their own sub-tasks) of this task.",
        export_string_translation=False,
    )
    effective_client_hours = fields.Float(
        "Effective Client Time", compute="compute_effective_client_hours", compute_sudo=True, store=True
    )

    @api.depends("timesheet_ids.client_time")
    def compute_effective_client_hours(self):
        if not any(self._ids):
            for task in self:
                task.effective_client_hours = sum(task.timesheet_ids.mapped("client_time"))
            return
        timesheet_read_group = self.env["account.analytic.line"]._read_group(
            [("task_id", "in", self.ids)], ["task_id"], ["client_time:sum"]
        )
        timesheets_per_task = {task.id: amount for task, amount in timesheet_read_group}
        for task in self:
            task.effective_client_hours = timesheets_per_task.get(task.id, 0.0)

    @api.depends("allocated_hours", "project_id.client_percentage")
    def compute_project_sharing_client_timesheets(self):
        subtask_ids_per_task_id = self.sudo().with_context(active_test=False)._get_subtask_ids_per_task_id()
        all_task_ids = set.union(set(), *subtask_ids_per_task_id.values(), self.ids)
        timesheet_read_group = (
            self.env["account.analytic.line"]
            .sudo()
            ._read_group(
                [
                    ("project_id", "!=", False),
                    ("task_id", "in", list(all_task_ids)),
                    (
                        "validated",
                        "in",
                        [
                            True,
                            self.env["ir.config_parameter"]
                            .sudo()
                            .get_param(
                                "sale.invoiced_timesheet",
                                {
                                    "effective_hours": "portal_effective_client_hours",
                                },
                            )
                            == "approved",
                        ],
                    ),
                ],
                ["task_id"],
                ["client_time:sum"],
            )
        )
        timesheets_per_task = {task.id: client_time_sum for task, client_time_sum in timesheet_read_group}
        for task in self:
            effective_client_hours = timesheets_per_task.get(task.id, 0.0)
            subtask_effective_client_hours = sum(
                timesheets_per_task.get(subtask_id, 0.0) for subtask_id in subtask_ids_per_task_id.get(task.id, [])
            )
            total_client_hours_spent = effective_client_hours + subtask_effective_client_hours
            task.portal_effective_client_hours = effective_client_hours
            task.portal_subtask_client_effective_hours = subtask_effective_client_hours
            task.portal_total_client_hours_spent = total_client_hours_spent

    @api.depends("child_ids.effective_client_hours", "child_ids.subtask_client_effective_hours")
    def compute_subtask_client_effective_hours(self):
        for task in self.with_context(active_test=False):
            task.subtask_client_effective_hours = sum(
                child_task.effective_client_hours + child_task.subtask_client_effective_hours
                for child_task in task.child_ids
            )

    @api.depends("effective_client_hours", "subtask_client_effective_hours")
    def compute_client_total_hours_spent(self):
        for task in self:
            task.total_client_hours_spent = task.effective_client_hours + task.subtask_client_effective_hours

    def _get_portal_total_hours_dict(self):
        result = super()._get_portal_total_hours_dict()
        if not result or not (timesheetable_tasks := self.filtered("allow_timesheets")):
            return result
        result["effective_hours"] = sum(self.filtered("allow_timesheets").mapped("effective_client_hours"))
        return result
