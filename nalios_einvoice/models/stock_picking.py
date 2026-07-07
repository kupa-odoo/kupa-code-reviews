# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    date_desiree = fields.Datetime("Desired Date")

    def _reorder_move_lines(self):
        for picking in self:
            if not picking.move_ids:
                continue
            sorted_moves = sorted(
                picking.move_ids,
                key=lambda lines: [int(code) for code in (lines.product_id.default_code or '0').split('.') if code.isdigit()]
            )
            for i, move in enumerate(sorted_moves):
                move.with_context(skip_reorder=True).sequence = i + 1


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        move = super().create(vals_list)
        if move.picking_id and not move.env.context.get('skip_reorder'):
            move.picking_id._reorder_move_lines()
        return move

    def write(self, vals):
        if self.env.context.get('skip_reorder'):
            return super().write(vals)
        res = super().write(vals)
        pickings = self.mapped('picking_id')
        if pickings:
            pickings._reorder_move_lines()
        return res
