import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class PoOverdue extends Component {
    static template = "FNT_sale_purchase_followup.widget_view";
    static props = {
        ...standardFieldProps,
    };
}

export const poOverdue = {
    component: PoOverdue,
};

registry.category("fields").add("po_overdue", poOverdue);
