/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";


patch(ProductScreen.prototype, {
    getNumpadButtons() {
        const buttons = super.getNumpadButtons(...arguments);
        return buttons.map((button) => {
            const isRestrictedRole = this.pos.cashier._role === "sale_assistant";
            if (button.value === "discount") {
                button.disabled = !this.pos.config.manual_discount || isRestrictedRole;
            }
            if (button.value === "price") {
                button.disabled = !this.pos.cashierHasPriceControlRights() || isRestrictedRole;
            }
            return button;
        });
    },
});
