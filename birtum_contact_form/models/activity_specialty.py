# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ActivitySpecialty(models.Model):
    _name = "activity.specialty"
    _description = "Activity Speciality"

    name = fields.Char(required=True, string="Speciality")
    active = fields.Boolean(default=True)
