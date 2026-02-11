# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    is_international =  fields.Boolean("Is International")
