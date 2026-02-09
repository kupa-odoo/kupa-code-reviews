# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"
    _unique_company_code = models.Constraint(
        "unique (company_code)",
        "Company Code must be unique across all companies.",
    )

    # Override field
    company_code = fields.Char(
        size=4,
        required=True,
        copy=False,
        default=lambda self: self._get_default_company_code(),
    )

    @api.constrains("company_code")
    def _check_company_code(self):
        for company in self.filtered(lambda company: company.company_code):
            if not company.company_code.isalnum():
                raise ValidationError(
                    self.env._(
                        "Company Code must consist of exactly 4 alphanumeric characters (e.g. 0001, 1005, Z001)."
                    )
                )

    @api.model
    def _get_default_company_code(self):
        companies_code = self.search([("company_code", "!=", False)]).mapped("company_code")
        numeric_codes = [int(code) for code in companies_code if code.isdigit() and len(code) == 4]
        return str((max(numeric_codes) if numeric_codes else 0) + 1).zfill(4)
