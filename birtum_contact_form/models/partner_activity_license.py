# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PartnerActivityLicense(models.Model):
    _name = "partner.activity.license"
    _description = "Activity License"
    _rec_name = "license_name"

    activity_id = fields.Many2one(
        "partner.activity",
        required=True,
        ondelete="cascade",
    )
    license_name = fields.Selection(
        [
            ("city", "City Council License"),
            ("tourism", "Tourism License"),
            ("health", "Health License"),
        ],
        required=True,
    )
    license_number = fields.Char()
    status = fields.Selection(
        [
            ("in_progress", "In Progress"),
            ("granted", "Granted"),
        ],
        string="License Status",
        required=True,
    )
    start_date = fields.Date()
    grant_date = fields.Date()

    @api.constrains("license_number")
    def _check_license_number(self):
        for record in self:
            if record.license_number and not re.match(r"^[A-Za-z0-9]+$", record.license_number):
                raise ValidationError("License Number must be alphanumeric (letters and numbers only).")
