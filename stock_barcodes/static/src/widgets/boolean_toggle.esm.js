/* @odoo-module */

import {BooleanToggleField} from "@web/views/fields/boolean_toggle/boolean_toggle_field";
import {onMounted} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useBus} from "@web/core/utils/hooks";

/**
 * Safe idle callback polyfill: falls back to setTimeout when not available.
 */
function safeRequestIdleCallback(cb) {
    if (typeof window.requestIdleCallback === "function") {
        return window.requestIdleCallback(cb);
    }
    return window.setTimeout(cb, 0);
}

/**
 * Small DOM helpers (no jQuery).
 */
function q1(selector, root = document) {
    return root.querySelector(selector);
}

export class BarcodeBooleanToggle extends BooleanToggleField {
    setup() {
        super.setup();

        // Cache commonly used state from the form model (defensive: keep guards)
        const rootModel = this.env?.model?.root;
        this.data = rootModel?.data || {};
        this.show_form_scan = Boolean(this.data.show_form_scan);

        // Ensure initial UI sync on mount
        onMounted(() => {
            this.enableFormEdit(this.props.value, true);
        });

        // React to external bus events to toggle edit mode
        useBus(this.env.bus, "enableFormEditBarcode", () => {
            this.enableFormEdit(true, true);
        });
        useBus(this.env.bus, "disableFormEditBarcode", () => {
            this.enableFormEdit(false, true);
        });
    }

    /*
     * This is needed because, whenever we click the checkbox to enter data
     * manually, the checkbox will be focused; when we scan the barcode afterwards,
     * it could block the python on_barcode_scanned function.
     */
    onChange(newValue) {
        super.onChange(newValue);
        // We can't blur during the same event tick; defer a bit
        safeRequestIdleCallback(() => {
            const active = document.activeElement;
            if (active && typeof active.blur === "function") {
                active.blur();
            }
        });
        this.enableFormEdit(newValue);
    }

    /**
     * Toggle the visibility of the manual form container and adjust
     * the inventory kanban container classes accordingly.
     *
     * @param {Boolean} newValue
     * @param {Boolean} [editAction=false] force toggle when called from bus/init
     */
    enableFormEdit(newValue, editAction = false) {
        // Only act for the intended field or explicit external action
        if (this.props.name !== "manual_entry" && !editAction) {
            return;
        }

        // NOTE: Selector kept as in original code. If the class name had a typo
        // (oe_stock_barcordes_content), consider correcting it in your templates
        // to "oe_stock_barcodes_content" and update this selector accordingly.
        const formEdit = q1("div.oe_stock_barcordes_content > div.scan_fields");
        const invKanban = q1("div[name='inventory_quant_ids'] div.o_kanban_renderer");

        // If we find the inventory kanban, ensure base class when form is missing or disabled
        if (!formEdit || this.show_form_scan) {
            if (invKanban) {
                invKanban.classList.add("inventory_quant_ids_without_form");
                invKanban.classList.remove("inventory_quant_ids_with_form");
            }
            return;
        }

        // Toggle visibility of manual form
        if (newValue) {
            formEdit.classList.remove("d-none");
            if (invKanban) {
                invKanban.classList.add("inventory_quant_ids_with_form");
                invKanban.classList.remove("inventory_quant_ids_without_form");
            }
        } else {
            formEdit.classList.add("d-none");
            if (invKanban) {
                invKanban.classList.remove("inventory_quant_ids_with_form");
                invKanban.classList.add("inventory_quant_ids_without_form");
            }
        }
    }
}

const barcodeBooleanToggle = {
    displayName: "Barcode Boolean Toggle",
    component: BarcodeBooleanToggle,
    // Was [""] -> fix for proper field binding
    supportedTypes: ["boolean"],
    extractProps: ({attrs}) => ({
        name: attrs.name,
    }),
};

registry.category("fields").add("barcode_boolean_toggle", barcodeBooleanToggle);
