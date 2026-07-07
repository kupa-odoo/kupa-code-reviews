# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _unique_project_number = models.Constraint(
        "unique (project_number)",
        "Project Number must be unique.",
    )

    project_number = fields.Char(
        string="Project Number",
        copy=False,
        size=10
    )

    master_project = fields.Char(
        string="Master Project",
        compute="_compute_master_project",
        store=True,
        index=True
    )

    @api.depends('project_number')
    def _compute_master_project(self):
        for rec in self:
            rec.master_project = rec.project_number[:6] if rec.project_number and len(rec.project_number) >= 6 else False

    @api.depends("name", "project_number")
    @api.depends_context("use_project_number")
    def _compute_display_name(self):
        super()._compute_display_name()
        use_project_number = self.env.context.get("use_project_number")
        for rec in self:
            rec.display_name = rec.project_number if use_project_number else rec.name or ""
