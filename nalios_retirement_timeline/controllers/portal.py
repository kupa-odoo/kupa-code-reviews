# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalCustom(CustomerPortal):

   def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        projects = request.env.user.partner_id.project_ids
        investments = projects.mapped('investment_ids')
        next_investment = investments.filtered(
            lambda investment : not investment.added_to_so
        ).sorted(key=lambda inv:inv.date)
        values['next_investment'] = next_investment[:1]
        return values
