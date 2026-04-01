/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { PercentageField } from "@web/views/fields/percentage/percentage_field";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";


export class ConfirmPercentageField extends PercentageField {
    static template = "sotelo_cretification.ConfirmPercentageField";
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.notification = useService("notification");
    }

    onChange(ev) {
        ev.stopPropagation()
        const newValue = ev.target.value;
        const currentValue = this.props.record.data[this.props.name]
        const isFirst = this.props.record.model.root.data.is_first_certification;
        if (!isFirst) {
            this.notification.add(
                _t("You can update percentage only for the first certification."),
                { type: "warning" }
            );

            ev.target.value = currentValue * 100;
            return;
        }

        if (parseFloat(newValue) < 0 || parseFloat(newValue) > 100) {
            this.notification.add(
                _t("The percenatge value must be from 0 to 100"),
                { type: "warning" }
            );
            ev.target.value = currentValue * 100;
            return;
        }

        this.dialogService.add(ConfirmationDialog, {
            body: _t("Are you sure you want to make change this value to %s %%?", newValue),
            confirmLabel: _t("Yes, Change it"),
            cancelLabel: _t("No, Keep original"),
            confirm: async () => {
                const currentValue = this.props.record.data.is_prev_accumulated_changed;
                await this.props.record.update({
                    [this.props.name]: parseFloat(newValue) / 100,
                    is_prev_accumulated_manual : true,
                    is_prev_accumulated_changed: !currentValue
                }, { save: true });
            },
            cancel: async () => {
                ev.target.value = currentValue * 100;
            },
        });
    }
}

registry.category("fields").add("confirm_percentage", {
    component: ConfirmPercentageField,
});
