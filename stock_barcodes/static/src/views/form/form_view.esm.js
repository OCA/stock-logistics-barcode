/** @odoo-module */
/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {StockBarcodesFormController} from "./form_controller.esm";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

export const StockBarcodesFormView = {
    ...formView,
    Controller: StockBarcodesFormController,
};

registry.category("views").add("stock_barcodes_form", StockBarcodesFormView);
