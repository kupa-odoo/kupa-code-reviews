# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    _check_so_followup_interval_positive = models.Constraint(
        "CHECK(so_followup_interval > 0)",
        "SO Follow-up Interval must be greater than zero.",
    )

    so_followup_interval = fields.Integer(
        string="SO Follow-up Interval (Days)",
        default=15,
    )
