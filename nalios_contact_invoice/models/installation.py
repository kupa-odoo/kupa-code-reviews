# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.osv import expression


class Installation(models.Model):
    _inherit="installations"

    def _get_invoice_domain(self):
        self.ensure_one()
        return expression.AND([
            [('task_id', '!=', False)],
            expression.OR([
                [('partner_id', '=', self.contact_intervention.id)],
                [('partner_shipping_id', '=', self.contact_intervention.id)],
            ])
        ])

    def action_view_invoices(self):
        self.ensure_one()
        action = super().action_view_invoices()
        action['domain'] = self._get_invoice_domain()
        return action

    def _compute_invoice_count(self):
        super()._compute_invoice_count()
        for record in self:
            if not record.contact_intervention:
                record.invoice_count = 0
                continue
            record.invoice_count = self.env['account.move'].search_count(record._get_invoice_domain())
