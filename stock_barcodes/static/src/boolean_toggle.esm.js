/** @odoo-module */
/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {BooleanToggleField} from "@web/views/fields/boolean_toggle/boolean_toggle_field";
import {registry} from "@web/core/registry";

class BarcodeBooleanToggleField extends BooleanToggleField {
    onChange(newValue) {
        super.onChange(newValue);
        requestIdleCallback(() => {
            document.activeElement.blur();
        });
    }
}

registry.category("fields").add("barcode_boolean_toggle", BarcodeBooleanToggleField);
