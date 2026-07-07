from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    certification_user_ids = fields.Many2many(
        'res.users',
        string="Allowed Certification Users",
        related="company_id.certification_user_ids",
        readonly=False
    )
