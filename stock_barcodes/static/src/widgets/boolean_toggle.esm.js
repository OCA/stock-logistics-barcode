/** @odoo-module */
/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {BooleanToggleField} from "@web/views/fields/boolean_toggle/boolean_toggle_field";
import {onMounted} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useBus} from "@web/core/utils/hooks";

class BarcodeBooleanToggleField extends BooleanToggleField {
    setup() {
        super.setup();
        onMounted(() => {
            this.enableFormEdit(this.props.value, true);
        });

        useBus(this.env.bus, "enableFormEditBarcode", () =>
            this.enableFormEdit(true, true)
        );
        useBus(this.env.bus, "disableFormEditBarcode", () =>
            this.enableFormEdit(false, true)
        );
    }

    /*
    This is needed because, whenever we click the checkbox to enter data
    manually, the checkbox will be focused causing that when we scan the
    barcode afterwards, it will not perform the python on_barcode_scanned
    function.
    */
    onChange(newValue) {
        super.onChange(newValue);
        // We can't blur an element on its onchange event
        // we need to wait for the event to finish (thus
        // requestIdleCallback)
        requestIdleCallback(() => {
            document.activeElement.blur();
        });
        this.enableFormEdit(newValue);
    }

    enableFormEdit(newValue, editAction = false) {
        // Enable edit form
        if (this.props.name === "manual_entry" || editAction) {
            const $form_edit = $("div.oe_stock_barcordes_content > div.scan_fields");
            const $div_inventory_quant_ids = $("div[name='inventory_quant_ids']").find(
                "div.o_kanban_renderer"
            );
            if ($form_edit.length > 0) {
                if (newValue) {
                    $form_edit.removeClass("d-none");
                    $div_inventory_quant_ids.addClass("inventory_quant_ids_with_form");
                    $div_inventory_quant_ids.removeClass(
                        "inventory_quant_ids_without_form"
                    );
                } else {
                    $form_edit.addClass("d-none");
                    $div_inventory_quant_ids.removeClass(
                        "inventory_quant_ids_with_form"
                    );
                    $div_inventory_quant_ids.addClass(
                        "inventory_quant_ids_without_form"
                    );
                }
            } else {
                $div_inventory_quant_ids.addClass("inventory_quant_ids_without_form");
            }
        }
    }
}

registry.category("fields").add("barcode_boolean_toggle", BarcodeBooleanToggleField);
