/** @odoo-module */
/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {NumericStep} from "@web_widget_numeric_step/numeric_step.esm";
import {isAllowedBarcodeModel} from "./barcodes_models_utils.esm";
import {patch} from "@web/core/utils/patch";

patch(NumericStep.prototype, "Adds barcode event handling and focus", {
    _onFocus() {
        if (isAllowedBarcodeModel(this.props.record.resModel)) {
            this.inputRef.el.select();
        }
    },

    _onKeyDown(ev) {
        if (isAllowedBarcodeModel(this.props.record.resModel) && ev.keyCode === 13) {
            const action_confirm = document.querySelector(
                "button[name='action_confirm']"
            );

            if (action_confirm) {
                action_confirm.click();
                return;
            }

            const action_confirm_force = document.querySelector(
                "button[name='action_force_done']"
            );

            if (action_confirm_force) {
                action_confirm_force.click();
                return;
            }
        }
        this._super(...arguments);
    },
});
//
// odoo.define("stock_barcodes.web_widget_numeric_step.field", function (require) {
//     "use strict";
//
//     const BasicController = require("web.BasicController");
//     const NumericStep = require("web_widget_numeric_step.field");
//     const BarcodesModelsMixin = require("stock_barcodes.BarcodesModelsMixin");
//
//     NumericStep.include(BarcodesModelsMixin);
//     NumericStep.include({
//         /**
//          * @override
//          */
//         init: function () {
//             this._super.apply(this, arguments);
//             this._is_valid_barcode_model = this._isAllowedBarcodeModel(this.model);
//             if (this._is_valid_barcode_model) {
//                 // Controller base is used when the renderer its initialized by a field
//                 this._controller_base = this.findAncestor((parent) => {
//                     return parent instanceof BasicController;
//                 });
//             }
//         },
//
//         /**
//          * Avoid intercept events in valid barcodes models.
//          * This is necessary to get the event in the controller.
//          *
//          * @override
//          */
//         _onKeyDown: function (ev) {
//             if (this._is_valid_barcode_model && ev.keyCode === $.ui.keyCode.ENTER) {
//                 if (this._controller_base) {
//                     ev.stopPropagation();
//                     this._controller_base._onDocumentKeyDown(ev);
//                 }
//             } else {
//                 this._super.apply(this, arguments);
//             }
//         },
//     });
// });
