# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ActivityType(models.Model):
    _name = "activity.type"
    _description = "Activity Type"

    name = fields.Char(required=True, string="Activity Type")
    active = fields.Boolean(default=True)
