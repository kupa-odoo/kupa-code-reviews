# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from collections import defaultdict

from odoo import fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_master_company_active = fields.Boolean(compute="_compute_is_master_company_active")

    def _compute_is_master_company_active(self):
        """Identify if user is currently in master company."""
        for partner in self:
            partner.is_master_company_active = self.env.company.is_master_company

    def action_sync_partner_accounts_from_master(self):
        """Sync partner Receivable/Payable accounts and some other fields from master to child companies."""

        syncable_companies = self.env["res.company"].sudo().search([
            ("exclude_from_partner_sync", "=", False)
        ])

        master_company = syncable_companies.filtered(lambda company: company.is_master_company)
        if not master_company:
            raise UserError(self.env._("No Master Company defined."))

        child_companies = syncable_companies - master_company
        all_company_ids = syncable_companies.ids

        self._validate_partners_before_sync()

        master_accounts = self.mapped("property_account_receivable_id") | self.mapped("property_account_payable_id")
        account_maps = self._map_accounts_by_company(
            master_accounts,
            all_company_ids,
        )

        payment_terms = self.mapped("property_payment_term_id") | self.mapped("property_supplier_payment_term_id")
        fiscal_positions = self.mapped("property_account_position_id")
        pricelists = self.mapped("property_product_pricelist")

        payment_term_map = self._map_records_by_company("account.payment.term", payment_terms, all_company_ids)
        fiscal_position_map = self._map_records_by_company("account.fiscal.position", fiscal_positions, all_company_ids)
        pricelist_map = self._map_records_by_company("product.pricelist", pricelists, all_company_ids)

        for partner in self:
            is_invalid = not (partner.is_company or not partner.parent_id)

            if is_invalid:
                _logger.warning(
                    "Partner '%s' is invalid for account sync (has parent and not a company). "
                    "Skipping account fields but syncing others.",
                    partner.display_name
                )

            receivable_master = partner.property_account_receivable_id
            payable_master = partner.property_account_payable_id

            receivable_map = account_maps.get(receivable_master.id, {}) if receivable_master else {}
            payable_map = account_maps.get(payable_master.id, {}) if payable_master else {}

            synced = []
            partial = []
            skipped = []

            for company in child_companies:
                vals = {}
                missing = []

                if not is_invalid:
                    receivable_val = self._get_partner_account_val(receivable_master, receivable_map, company, "receivable account", missing)
                    payable_val = self._get_partner_account_val(payable_master, payable_map, company, "payable account", missing)

                    if receivable_val is not None:
                        vals["property_account_receivable_id"] = receivable_val

                    if payable_val is not None:
                        vals["property_account_payable_id"] = payable_val
                else:
                    missing.append("account sync skipped (invalid partner)")

                # === Payment Term ===
                customer_pt = self._get_mapped_value(payment_term_map, partner.property_payment_term_id, company)
                supplier_pt = self._get_mapped_value(payment_term_map, partner.property_supplier_payment_term_id, company)
                self._apply_mapped(vals, missing, "property_payment_term_id", "customer payment term", customer_pt, partner.property_payment_term_id)
                self._apply_mapped(vals, missing, "property_supplier_payment_term_id", "supplier payment term", supplier_pt, partner.property_supplier_payment_term_id)

                # === Fiscal Position ===
                fiscal_position = self._get_mapped_value(fiscal_position_map, partner.property_account_position_id, company)
                self._apply_mapped(vals, missing, "property_account_position_id", "fiscal position", fiscal_position, partner.property_account_position_id)

                # === Pricelist ===
                pricelist = self._get_mapped_value(pricelist_map, partner.property_product_pricelist, company)
                self._apply_mapped(vals, missing, "property_product_pricelist", "pricelist", pricelist, partner.property_product_pricelist)

                # === Other Fields ===
                vals.update({
                    "receipt_reminder_email": partner.receipt_reminder_email,
                    "reminder_date_before_receipt": partner.reminder_date_before_receipt,
                    "property_purchase_currency_id": partner.property_purchase_currency_id.id or False
                })

                if vals:
                    partner.with_company(company).sudo().write(vals)
                    if missing:
                        partial.append(f"{company.display_name} (missing {', '.join(missing)})")
                    else:
                        synced.append(company.display_name)
                else:
                    skipped.append(company.display_name)

            _logger.info(
                "Partner '%s' sync summary: %s full, %s partial, %s skipped (Total: %s)",
                partner.display_name, len(synced), len(partial), len(skipped), len(child_companies),
            )

            if partial:
                _logger.warning(
                    "Partner '%s' partially synced for: %s",
                    partner.display_name, "; ".join(partial),
                )

            if skipped:
                _logger.warning(
                    "Partner '%s' skipped for: %s",
                    partner.display_name, "; ".join(skipped),
                )

        _logger.info("Partner account sync completed.")
        return True

    # === Helper methods ====

    def _validate_partners_before_sync(self):
        """Ensure all partner Receivable/Payable accounts belong to the Master Company before syncing."""
        errors = []
        for partner in self:
            for field, label, is_account in [
                ("property_account_receivable_id", "receivable", True),
                ("property_account_payable_id", "payable", True),
                ("property_payment_term_id", "customer payment term", False),
                ("property_supplier_payment_term_id", "supplier payment term", False),
                ("property_account_position_id", "fiscal position", False),
                ("property_product_pricelist", "pricelist", False)
            ]:
                record = partner[field]

                if not record: continue

                if is_account:
                    if not record.has_master_company:
                        errors.append(
                            f"Partner '{partner.display_name}': {label} account "
                            f"'{record.display_name}' does not belong to Master Company."
                        )
                else:
                    if record.company_id and not record.company_id.is_master_company:
                        errors.append(
                            f"Partner '{partner.display_name}': {label} "
                            f"'{record.display_name}' does not belong to Master Company or is not global."
                        )

        if errors:
            raise UserError("\n".join(errors))

    def _map_accounts_by_company(self, master_accounts, all_company_ids):
        """
        Build mapping for multiple master accounts at once.

        Returns:
            {
                master_account_id: {company_id: account_record}
            }
        """
        if not master_accounts:
            return {}

        Account = self.env["account.account"].sudo().with_context(allowed_company_ids=all_company_ids)
        accounts = Account.browse(master_accounts.ids)
        accounts |= accounts.with_context(allowed_company_ids=all_company_ids).child_account_ids

        # result[master_id][company_id] returns mapped account or False.
        result = defaultdict(lambda: defaultdict(lambda: False))

        for acc in accounts:
            if len(acc.company_ids) != 1:
                _logger.warning(
                    "Account '%s' (id=%s) belongs to %s companies - skipping.",
                    acc.display_name,
                    acc.id,
                    len(acc.company_ids),
                )
                continue

            # determine which master this account belongs to
            master_id = acc.parent_account_id.id or acc.id
            result[master_id][acc.company_ids.id] = acc

        return {k: dict(v) for k, v in result.items()}

    def _get_partner_account_val(self, master_account, account_map, company, field_label, missing):
        """
        Return the field value to write for a single account field on a child company,
        or None if no mapped account was found (appends to missing in that case).
        """
        if not master_account:
            return False
        acc = account_map.get(company.id)
        if acc:
            return acc.id
        missing.append(field_label)
        return None

    def _map_records_by_company(self, model, master_records, all_company_ids):
        if not master_records:
            return {}

        Model = self.env[model].sudo().with_context(allowed_company_ids=all_company_ids)

        names = list(set(master_records.mapped("name")))
        all_recs = Model.search([
            ("name", "in", names),
            ("company_id", "in", all_company_ids)
        ])

        # Build lookup: {name: {company_id: record}}
        lookup = defaultdict(dict)
        for rec in all_recs:
            lookup[rec.name][rec.company_id.id] = rec

        result = {}
        for record in master_records:
            name = record.name
            if not record.company_id:
                result[name] = {cid: record for cid in all_company_ids}
            else:
                company_map = lookup.get(name, {})
                result[name] = {
                    cid: company_map.get(cid, False)
                    for cid in all_company_ids
                }

        return result

    def _get_mapped_value(self, mapping, master_record, company):
        if not master_record:
            return False
        rec = mapping.get(master_record.name, {}).get(company.id)
        return rec.id if rec else False

    def _apply_mapped(self, vals, missing, field, label, value, original):
        if value:
            vals[field] = value
        elif original:
            missing.append(label)
