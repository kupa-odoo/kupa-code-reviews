/** @odoo-module **/

import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

export class PortalSaleUpload extends Interaction {
    static selector = ".o_portal_sale_upload";
    dynamicContent = {
        ".o_toggle_manual": {"t-on-change": this.toggleManual},
    };

    start() {
        this.toggleManual();
    }

    toggleManual() {
        const checkbox = document.querySelector(".o_toggle_manual");
        const manualWrapper = document.querySelector(".o_manual_date_wrapper");
        const fileWrapper = document.querySelector(".o_file_wrapper");
        const manualInput = document.querySelector(".o_manual_date");
        const fileInput = document.querySelector(".o_upload_file");

        if (checkbox.checked) {
            manualWrapper.style.display = "block";
            fileWrapper.style.display = "none";
            manualInput.setAttribute("required", "required");
            fileInput.removeAttribute("required");
            fileInput.value = "";
        } else {
            manualWrapper.style.display = "none";
            fileWrapper.style.display = "block";
            fileInput.setAttribute("required", "required");
            manualInput.removeAttribute("required");
            manualInput.value = "";
        }
    }
}

registry.category("public.interactions").add("FNT_sale_purchase_followup.sale_upload", PortalSaleUpload);
