# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class AccountMove(models.Model):
    _inherit="account.move"

    certfication_id = fields.Many2one("project.certification")

    def action_view_certification(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Certification'),
            'res_model': 'project.certification',
            'view_mode': 'form',
            'res_id': self.certfication_id.id,
            'target': 'current'
        }
