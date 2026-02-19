# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    certification_product = fields.Many2one("product.product")
    invoice_deduction_product = fields.Many2one("product.product")

    def action_view_certifications(self):
        self.ensure_one()
        certifications = self.env['project.certification'].search([('project_id', '=', self.id)], limit=2)
        action = {
            'type': 'ir.actions.act_window',
            'name': self.env._('Certifications'),
            'res_model': 'project.certification',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id
            }
        }
        if len(certifications) == 1:
            action.update({
                'res_id': certifications.id,
                'view_mode': 'form'
            })
        return action
