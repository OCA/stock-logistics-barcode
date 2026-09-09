/** @odoo-module **/

/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {NumericStep} from "@web_widget_numeric_step/numeric_step.esm";
import {isAllowedBarcodeModel} from "../utils/barcodes_models_utils.esm";
import {patch} from "@web/core/utils/patch";

/**
 * Patch: improve UX for numeric step fields when used in barcode-enabled models.
 * - Auto-select all content on focus.
 * - Pressing Enter triggers stock confirm / force-done actions automatically.
 * Compatible with Odoo 16–18.
 */
patch(NumericStep.prototype, {
    /**
     * Auto-select the numeric input value when focusing the field.
     */
    _onFocus() {
        try {
            if (
                isAllowedBarcodeModel(this.props?.record?.resModel) &&
                this.inputRef?.el &&
                typeof this.inputRef.el.select === "function"
            ) {
                this.inputRef.el.select();
            }
        } catch {
            // Defensive: ignore any runtime errors (e.g., input not yet mounted)
        }
    },

    /**
     * Handle Enter key presses in numeric fields for barcode flows.
     */
    _onKeyDown(ev) {
        // Use modern key detection
        if (isAllowedBarcodeModel(this.props?.record?.resModel) && ev.key === "Enter") {
            const confirmBtn = document.querySelector("button[name='action_confirm']");
            if (confirmBtn instanceof HTMLElement) {
                confirmBtn.click();
                ev.preventDefault();
                ev.stopPropagation();
                return;
            }

            const forceBtn = document.querySelector("button[name='action_force_done']");
            if (forceBtn instanceof HTMLElement) {
                forceBtn.click();
                ev.preventDefault();
                ev.stopPropagation();
                return;
            }
        }

        // Fallback to parent behavior
        super._onKeyDown?.(ev);
    },
});
