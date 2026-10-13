/** @odoo-module **/

/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {formView} from "@web/views/form/form_view";
import {StockBarcodesFormController} from "./form_controller.esm";

/**
 * Alias of the standard Form view with a custom Controller.
 * Use it via `js_class="stock_barcodes_form"` in your <form> arch.
 */
export const StockBarcodesFormView = {
    ...formView,
    type: "form", // Be explicit for future-proofing
    Controller: StockBarcodesFormController,
};

registry.category("views").add("stock_barcodes_form", StockBarcodesFormView);
