# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    certification_product = fields.Many2one("product.product")
    invoice_deduction_product = fields.Many2one("product.product")
    certification_ids = fields.One2many(
        "project.certification",
        "project_id",
        string="Certifications"
    )

    def action_view_certifications(self):
        self.ensure_one()
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
        if len(self.certification_ids) == 1:
            action.update({
                'res_id': self.certification_ids.id,
                'view_mode': 'form'
            })
        return action
