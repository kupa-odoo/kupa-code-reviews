from odoo import Command, models

class SaleOrderLine(models.Model):
    _inherit="sale.order.line"

    def _timesheet_create_project_prepare_values(self):
        values = super()._timesheet_create_project_prepare_values()
        project_template = self.product_id.project_template_id
        if project_template.retirement_timeline_ids:
            timeline_vals = []
            for tl in project_template.retirement_timeline_ids:
                timeline_vals.append(Command.create({
                    'label': tl.label,
                    'ceiling': tl.ceiling,
                    'pct_invest': tl.pct_invest
                }))
            values['retirement_timeline_ids'] = timeline_vals
        return values
