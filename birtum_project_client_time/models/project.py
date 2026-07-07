# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_round
from odoo.tools.safe_eval import safe_eval


class ProjectProject(models.Model):
    _inherit = "project.project"

    client_percentage = fields.Float(string="Client Percentage")
    total_client_time = fields.Float(
        compute="compute_total_client_time",
        groups="hr_timesheet.group_hr_timesheet_user",
        string="Total Client Time",
        export_string_translation=False,
    )

    @api.depends("timesheet_ids", "timesheet_encode_uom_id")
    def compute_total_client_time(self):
        timesheets_read_group = self.env["account.analytic.line"]._read_group(
            [("project_id", "in", self.ids)],
            ["project_id", "product_uom_id"],
            ["client_time:sum"],
        )
        time_dict = defaultdict(list)
        for project, product_uom, client_time_sum in timesheets_read_group:
            time_dict[project.id].append((product_uom, client_time_sum))
        for project in self:
            total = 0.0
            for product_uom, client_time in time_dict.get(project.id, []):
                factor = (product_uom or project.timesheet_encode_uom_id).factor
                total += client_time * (1.0 if project.encode_uom_in_days else factor)
            total /= project.timesheet_encode_uom_id.factor
            project.total_client_time = float_round(total, precision_digits=2)

    def _prepare_timesheet_action(self, mode):
        """Set the context to control the visibility of the field in the UI."""
        action = super().action_project_timesheets()
        ctx = action.get("context") or {}
        if isinstance(ctx, str):
            ctx = safe_eval(ctx, {"active_id": self.id, "active_ids": self.ids})
        action["context"] = {**ctx, "timesheet_view_mode": mode}
        return action

    def action_project_timesheets_tracking(self):
        return self._prepare_timesheet_action("tracking")

    def action_project_timesheets_client(self):
        return self._prepare_timesheet_action("client")

    def _get_stat_buttons(self):
        """
        Add a new button to the Project Dashboard to display Client Time.
        Update the label of the existing Timesheet button by appending “Allocated” to the current button name.
        """
        buttons = super()._get_stat_buttons()
        if not self.allow_timesheets or not self.env.user.has_group("hr_timesheet.group_hr_timesheet_user"):
            return buttons

        encode_uom = self.env.company.timesheet_encode_uom_id
        uom_ratio = self.env.ref("uom.product_uom_hour").factor / encode_uom.factor
        client = round(self.total_client_time / uom_ratio)

        number = self.env._("%(client)s\nClient %(uom_name)s", client=round(client), uom_name=encode_uom.name)
        client_button = {
            "icon": "clock-o",
            "text": self.env._("Timesheets"),
            "number": number,
            "action_type": "object",
            "action": "action_project_timesheets",
            "show": True,
            "sequence": 2,
        }

        for index, button in enumerate(buttons):
            if button.get("text") == self.env._("Timesheets"):
                button["number"] = self.env._("%(original)s\nAllocated", original=button.get("number", ""))
                buttons.insert(index + 1, client_button)
                break
        else:
            buttons.append(client_button)

        return buttons
