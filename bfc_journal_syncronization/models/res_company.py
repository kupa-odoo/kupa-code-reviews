# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from odoo.exceptions import UserError


SYNC_FIELDS = [
    'type',
    'name',
    'code',
    'refund_sequence',
    'debit_sequence',
    'invoice_reference_type',
    'invoice_reference_model',
    'restrict_mode_hash_table',
    'active'
]

ALLOWED_JOURNAL_TYPES = ['sale', 'purchase', 'general']


class ResCompany(models.Model):
    _inherit = "res.company"

    journal_ids = fields.One2many(
        'account.journal',
        'company_id',
        context={"active_test": False},
        string="Comapny Journals"
    )

    def prepare_journal_parent_child_relation(self):
        self.ensure_one()
        self.env["account.journal"]._link_parent_journals_to_master(master_company=self)

    def sync_with_master_company_journals(self):
        Company = self.env["res.company"]
        Journal = self.env["account.journal"]

        master_company = Company.search([("is_master_company", "=", True)], limit=1)
        if not master_company:
            raise UserError(self.env._("Please define master company first!"))

        target_companies = self - master_company
        if not target_companies:
            return

        Journal = Journal.with_context(
            allowed_company_ids=(master_company | target_companies).ids,
            skip_company_sync=True,
            active_test=False,
        )

        master_journals = master_company.with_context(
            allowed_company_ids=(master_company | target_companies).ids,
        ).journal_ids.filtered(lambda journal: journal.type in ALLOWED_JOURNAL_TYPES)

        if not master_journals:
            return

        account_map = Journal._map_accounts_by_company(
            master_journals.mapped("default_account_id"),
            (master_company | target_companies).ids
        )

        for company in target_companies:

            child_journals = company.with_context(
                allowed_company_ids=(master_company | target_companies).ids,
            ).journal_ids

            by_code = {journal.code: journal for journal in child_journals}

            to_create = []

            for master in master_journals:
                existing_journal = by_code.get(master.code)
                child_default_account_id = Journal._get_child_account_id(
                    master.default_account_id,
                    account_map,
                    company
                ) or False

                vals = {field: master[field] for field in SYNC_FIELDS}

                vals.update({
                    "currency_id":master.currency_id.id,
                    "parent_journal_id": master.id
                })

                if child_default_account_id:
                    vals["default_account_id"] = child_default_account_id

                if existing_journal:
                    existing_journal.write(vals)
                    continue

                vals.update({
                    "company_id": company.id,
                })

                to_create.append((vals, child_default_account_id, master.default_account_id))

            # Batch Create
            if to_create:
                create_vals = [vals for vals, _, _ in to_create]
                created_journals = Journal.create(create_vals)

                for journal, (_, child_default_account_id, master_default_account) in zip(created_journals, to_create):
                    if not child_default_account_id and master_default_account:
                        journal.message_post(
                            body=self.env._(
                                "Journal created but Default Account were not synchronized because Account is missing for this company."
                            )
                        )
