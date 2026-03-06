# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Override field
    owner_name = fields.Char(
        compute="_compute_owner_name",
        store=True,
        readonly=False
    )

    @api.depends("partner_id")
    def _compute_owner_name(self):
        for rec in self:
            address = rec.partner_id.contact_address_ids[:1]
            rec.owner_name = address.owner_reference if address else False
