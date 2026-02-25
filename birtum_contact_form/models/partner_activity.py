# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PartnerActivity(models.Model):
    _name = "partner.activity"
    _description = "Associate Activity"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        ondelete="cascade",
    )
    activity_type_id = fields.Many2one(
        "activity.type",
        string="Activity",
        required=True,
    )
    category = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)],
        string="Category",
    )
    specialty_id = fields.Many2one(
        "activity.specialty",
        string="Speciality",
    )
    license_ids = fields.One2many(
        "partner.activity.license",
        "activity_id",
        string="Licenses",
    )
