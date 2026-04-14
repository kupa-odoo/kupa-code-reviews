from odoo import fields, models

class SaleOrder(models.Model):
    _inherit="sale.order"

    project_approved_done = fields.Boolean(string="Project Approved Used")

    def action_project_approved(self):
        for order in self.filtered(lambda so: so.team_id):
            sales_team = order.team_id
            if sales_team.section_name:
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'display_type': 'line_section',
                    'name': sales_team.section_name,
                })
            if sales_team.reimbursment_product:
                product = sales_team.reimbursment_product
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'product_uom_qty': 1,
                    'price_unit': product.list_price,
                })
            order.project_approved_done = True
