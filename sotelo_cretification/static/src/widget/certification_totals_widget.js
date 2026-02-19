/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formatMonetary } from "@web/views/fields/formatters";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";


export class CertificationTotal extends Component {
    static template = "sotelo_certification.widget_view";
    static props = {
        ...standardFieldProps,
    };

    formatMonetary(value) {
        return formatMonetary(value, {currencyId: this.props.record.data.currency_id.id});
    }
}

export const certificationTotal = {
    component: CertificationTotal,
};

registry.category("fields").add("certification-total", certificationTotal);
