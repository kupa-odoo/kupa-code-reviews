/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    get employeeIsAdmin() {
        const res = super.employeeIsAdmin
        const cashier = this.getCashier();
        return res || cashier._role === "sale_assistant"
    },
});
