/* @odoo-module */

/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {StockBarcodesFormController} from "./form_controller.esm";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

/**
 * Alias of the standard Form view with a custom Controller.
 * Use it via `js_class="stock_barcodes_form"` in your <form> arch.
 */
export const StockBarcodesFormView = {
    ...formView,
    // Be explicit for future-proofing
    type: "form",
    Controller: StockBarcodesFormController,
};

registry.category("views").add("stock_barcodes_form", StockBarcodesFormView);
