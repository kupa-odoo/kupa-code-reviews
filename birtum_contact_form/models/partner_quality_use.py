# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PartnerQualityUse(models.Model):
    _name = "partner.quality.use"
    _description = "Partner Quality Use"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        ondelete="cascade",
    )
    agreement = fields.Text("Description")
    signing_date = fields.Date()
    discharge_date = fields.Date()
    connected_fns = fields.Boolean(string="Connected To FNS")
    channel_manager = fields.Boolean()
    pms = fields.Boolean(string="PMS")
    website_with_fns = fields.Boolean(string="Website With FNS")
    notes = fields.Text()
    amount = fields.Float()
