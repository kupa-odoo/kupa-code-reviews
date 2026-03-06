# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StandardWork(models.Model):
    _inherit="standard.work"
    _order = "sequence, id"

    sequence = fields.Integer()
