# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit='project.project'

    retirement_timeline_ids = fields.One2many("retirement.timeline", "project_id")
    investment_ids = fields.One2many("investments.investment", "project_id")

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        for project in projects.filtered(lambda project: project.reinvoiced_sale_order_id):
            project.reinvoiced_sale_order_id.opportunity_id._compute_project_ids()

        return projects

    def write(self, vals):
        res = super().write(vals)
        if 'reinvoiced_sale_order_id' in vals:
            self.reinvoiced_sale_order_id.opportunity_id._compute_project_ids()
        return res
