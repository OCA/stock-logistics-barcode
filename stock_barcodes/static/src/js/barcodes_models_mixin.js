/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

// eslint-disable-next-line no-unused-vars
odoo.define("stock_barcodes.BarcodesModelsMixin", function (require) {
    "use strict";

    const BarcodesModelsMixin = {
        // Models allowed to have extra keybinding features
        _barcode_models: [
            "stock.barcodes.action",
            "stock.picking",
            "stock.picking.type",
            "wiz.candidate.picking",
            "wiz.stock.barcodes.new.lot",
            "wiz.stock.barcodes.read",
            "wiz.stock.barcodes.read.inventory",
            "wiz.stock.barcodes.read.picking",
            "wiz.stock.barcodes.read.todo",
        ],

        /**
         * Helper to know if the given model is allowed
         *
         * @private
         * @returns {Boolean}
         */
        _isAllowedBarcodeModel: function (model_name) {
            return this._barcode_models.indexOf(model_name) !== -1;
        },
    };

    return BarcodesModelsMixin;
});
