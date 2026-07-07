# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import SQL


class BudgetReport(models.Model):
    _inherit = 'budget.report'

    project_budget = fields.Float('Basebudget', readonly=True)
    expected_additional_value = fields.Float('Expected Additional Value', readonly=True)
    forecast = fields.Float('Available', readonly=True)
    cost_allocation = fields.Selection(
        [
            ("0", "-0 Project"),
            ("7", "-7 Early Phase"),
            ("8", "-8 Closing Postings"),
            ("9", "-9 Internal Services"),
        ],
        string="Cost Allocation",
        readonly=True
    )
    # Added from module ece_analytic_budget_stored
    achieved_amount_stored = fields.Float(string="Achieved (Stored)", help="Amount Billed/Invoiced.", readonly=True)

    def _get_bl_query(self, plan_fnames):
        return SQL(
            """
            SELECT CONCAT('bl', bl.id::TEXT) AS id,
                   bl.budget_analytic_id AS budget_analytic_id,
                   bl.id AS budget_line_id,
                   'budget.analytic' AS res_model,
                   bl.budget_analytic_id AS res_id,
                   bl.date_from AS date,
                   bl.date_to AS bl_date_to,
                   ba.name AS description,
                   bl.company_id AS company_id,
                   NULL AS user_id,
                   'budget' AS line_type,
                   bl.cost_allocation AS cost_allocation,
                   bl.budget_amount AS budget,
                   bl.project_budget AS project_budget,
                   bl.expected_additional_value AS expected_additional_value,
                   (bl.budget_amount - COALESCE(bl.achieved_amount_stored, 0)) AS forecast,
                   bl.achieved_amount_stored AS achieved_amount_stored,
                   0 + COALESCE(bl.achieved_amount_stored, 0) AS committed,  -- used in `account_budget_purchase`
                   0 + COALESCE(bl.achieved_amount_stored, 0) AS achieved,
                   CASE WHEN NOW() < bl.date_to AND NOW() > bl.date_from
                        THEN (((NOW()::DATE - bl.date_from::DATE + 1))/(bl.date_to::DATE - bl.date_from::DATE + 1)::FLOAT)*bl.budget_amount
                        WHEN NOW() < bl.date_from
                        THEN 0
                        ELSE bl.budget_amount
                   END AS theoretical,
                   %(plan_fields)s
              FROM budget_line bl
              JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
            """,
            plan_fields=SQL(', ').join(self.env['budget.line']._field_to_sql('bl', fname) for fname in plan_fnames)
        )

    def _get_aal_query(self, plan_fnames):
        return SQL(
            """
            SELECT CONCAT('aal', aal.id::TEXT) AS id,
                   bl.budget_analytic_id AS budget_analytic_id,
                   bl.id AS budget_line_id,
                   'account.analytic.line' AS res_model,
                   aal.id AS res_id,
                   aal.date AS date,
                   bl.date_to AS bl_date_to,
                   aal.name AS description,
                   aal.company_id AS company_id,
                   aal.user_id AS user_id,
                   'achieved' AS line_type,
                   bl.cost_allocation AS cost_allocation,
                   0 AS budget,
                   0 AS project_budget,
                   0 AS expected_additional_value,
                   aal.amount * CASE WHEN ba.budget_type = 'expense' THEN 1 ELSE -1 END AS forecast,  -- used in `account_budget_purchase`
                   0 AS achieved_amount_stored,
                   aal.amount * CASE WHEN ba.budget_type = 'expense' THEN -1 ELSE 1 END AS committed,  -- used in `account_budget_purchase`
                   aal.amount * CASE WHEN ba.budget_type = 'expense' THEN -1 ELSE 1 END AS achieved,
                   0 AS theoretical,
                   %(analytic_fields)s
              FROM account_analytic_line aal
         LEFT JOIN budget_line bl ON (bl.company_id IS NULL OR aal.company_id = bl.company_id)
                                 AND aal.date >= bl.date_from
                                 AND aal.date <= bl.date_to
                                 AND %(condition)s
         LEFT JOIN account_account aa ON aa.id = aal.general_account_id
         LEFT JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
             WHERE CASE
                       WHEN ba.budget_type = 'expense' THEN (
                           SPLIT_PART(aa.account_type, '_', 1) = 'expense'
                           OR (aa.account_type IS NULL AND aal.category NOT IN ('invoice', 'other'))
                           OR (aa.account_type IS NULL AND aal.category = 'other' AND aal.amount < 0)
                       )
                       WHEN ba.budget_type = 'revenue' THEN (
                           SPLIT_PART(aa.account_type, '_', 1) = 'income'
                           OR (aa.account_type IS NULL AND aal.category = 'other' AND aal.amount > 0)
                       )
                       ELSE TRUE
                   END
                   AND (SPLIT_PART(aa.account_type, '_', 1) IN ('income', 'expense') OR aa.account_type IS NULL)
            """,
            analytic_fields=SQL(', ').join(self.env['account.analytic.line']._field_to_sql('aal', fname) for fname in plan_fnames),
            condition=SQL(' AND ').join(SQL(
                "(%(bl)s IS NULL OR %(aal)s = %(bl)s)",
                bl=self.env['budget.line']._field_to_sql('bl', fname),
                aal=self.env['budget.line']._field_to_sql('aal', fname),
            ) for fname in plan_fnames)
        )

    def _get_pol_query(self, plan_fnames):
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit')
        qty_invoiced_table = SQL(
            """
               SELECT SUM(
                          CASE WHEN COALESCE(uom_aml.id != uom_pol.id, FALSE)
                               THEN ROUND(CAST((aml.quantity / uom_aml.factor) * uom_pol.factor AS NUMERIC), %(precision_digits)s)
                               ELSE COALESCE(aml.quantity, 0)
                          END
                          * CASE WHEN am.move_type = 'in_invoice' THEN 1
                                 WHEN am.move_type = 'in_refund' THEN -1
                                 ELSE 0 END
                      ) AS qty_invoiced,
                      pol.id AS pol_id
                 FROM purchase_order po
            LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
            LEFT JOIN account_move_line aml ON aml.purchase_line_id = pol.id
            LEFT JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN uom_uom uom_aml ON uom_aml.id = aml.product_uom_id
            LEFT JOIN uom_uom uom_pol ON uom_pol.id = pol.product_uom_id
                WHERE aml.parent_state = 'posted'
             GROUP BY pol.id
        """,
            precision_digits=precision_digits
        )
        return SQL(
            """
            SELECT (pol.id::TEXT || '-' || ROW_NUMBER() OVER (PARTITION BY pol.id ORDER BY pol.id)) AS id,
                   bl.budget_analytic_id AS budget_analytic_id,
                   bl.id AS budget_line_id,
                   'purchase.order' AS res_model,
                   po.id AS res_id,
                   po.date_order AS date,
                   bl.date_to AS bl_date_to,
                   pol.name AS description,
                   pol.company_id AS company_id,
                   po.user_id AS user_id,
                   'committed' AS line_type,
                   bl.cost_allocation AS cost_allocation,
                   0 AS budget,
                   0 AS project_budget,
                   0 AS expected_additional_value,
                   0 - COALESCE(pol.price_subtotal::FLOAT, pol.price_unit::FLOAT * pol.product_qty)
                        / COALESCE(NULLIF(pol.product_qty, 0), 1)
                        * (pol.product_qty - COALESCE(qty_invoiced_table.qty_invoiced, 0))
                        / po.currency_rate
                        * (a.rate)
                        * CASE WHEN ba.budget_type = 'both' THEN -1 ELSE 1 END AS forecast,
                   0 AS achieved_amount_stored,
                   COALESCE(pol.price_subtotal::FLOAT, pol.price_unit::FLOAT * pol.product_qty)
                        / COALESCE(NULLIF(pol.product_qty, 0), 1)
                        * (pol.product_qty - COALESCE(qty_invoiced_table.qty_invoiced, 0))
                        / po.currency_rate
                        * (a.rate)
                        * CASE WHEN ba.budget_type = 'both' THEN -1 ELSE 1 END AS committed,
                   0 AS achieved,
                   0 AS theoretical,
                   %(analytic_fields)s
              FROM purchase_order_line pol
         LEFT JOIN (%(qty_invoiced_table)s) qty_invoiced_table ON qty_invoiced_table.pol_id = pol.id
              JOIN purchase_order po ON pol.order_id = po.id AND po.state = 'purchase'
        CROSS JOIN JSONB_TO_RECORDSET(pol.analytic_json) AS a(rate FLOAT, %(field_cast)s)
         LEFT JOIN budget_line bl ON (bl.company_id IS NULL OR po.company_id = bl.company_id)
                                 AND po.date_order >= bl.date_from
                                 AND date_trunc('day', po.date_order) <= bl.date_to
                                 AND %(condition)s
         LEFT JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
             WHERE pol.product_qty > COALESCE(qty_invoiced_table.qty_invoiced, 0)
               AND ba.budget_type != 'revenue'
            """,
            analytic_fields=SQL(', ').join(self.env['account.analytic.line']._field_to_sql('a', fname) for fname in plan_fnames),
            qty_invoiced_table=qty_invoiced_table,
            field_cast=SQL(', ').join(SQL('%s FLOAT', SQL.identifier(fname)) for fname in plan_fnames),
            condition=SQL(' AND ').join(SQL(
                "(%(bl)s IS NULL OR %(a)s = %(bl)s)",
                bl=self.env['budget.line']._field_to_sql('bl', fname),
                a=self.env['budget.line']._field_to_sql('a', fname),
            ) for fname in plan_fnames)
        )

    @property
    def _table_query(self):
        self.env['account.move.line'].flush_model()
        self.env['budget.line'].flush_model()
        self.env['account.analytic.line'].flush_model()
        self.env['purchase.order.line'].flush_model()

        project_plan, other_plans = self.env['account.analytic.plan']._get_all_plans()
        plan_fnames = [
            fname
            for plan in project_plan | other_plans
            if (fname := plan._column_name()) in self
        ]
        return SQL(
            "%s UNION ALL %s UNION ALL %s",
            self._get_bl_query(plan_fnames),
            self._get_aal_query(plan_fnames),
            self._get_pol_query(plan_fnames),
        )
