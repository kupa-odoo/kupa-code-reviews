# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class DischargeReason(models.Model):
    _name = "discharge.reason"
    _description = "Discharge Reason"
    _check_unique_name = models.Constraint(
        "UNIQUE(name)",
        "Reason must be unique."
    )

    name = fields.Char(required=True, string="Discharge Reason")
    active = fields.Boolean(default=True)
