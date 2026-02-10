# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    followup_interval = fields.Integer(
        string="Followup Interval (in Days)",
        related="company_id.so_followup_interval",
        readonly=False,
    )
