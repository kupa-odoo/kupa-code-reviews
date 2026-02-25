# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class CompanyGroup(models.Model):
    _name = "company.group"
    _description = "Company Group"
    _check_unique_name = models.Constraint(
        "UNIQUE(name)",
        "Company Group must be unique."
    )

    name = fields.Char(required=True, copy=False, string="Compnay Group Name")
    active = fields.Boolean(default=True)
    group_number = fields.Integer()
