/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define("stock_barcodes.KanbanRenderer", function (require) {
    "use strict";

    const BasicController = require("web.BasicController");
    const KanbanRenderer = require("web.KanbanRenderer");
    const BarcodesModelsMixin = require("stock_barcodes.BarcodesModelsMixin");

    KanbanRenderer.include(BarcodesModelsMixin);
    KanbanRenderer.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this._is_valid_barcode_model = this._isAllowedBarcodeModel(
                this.state.model
            );
            if (this._is_valid_barcode_model) {
                // Controller base is used when the renderer its initialized by a field
                this._controller_base = this.findAncestor((parent) => {
                    return parent instanceof BasicController;
                });
            }
        },

        /**
         * Avoid intercept events in valid barcodes models.
         * This is necessary to get the event in the controller.
         *
         * @override
         */
        _onRecordKeyDown: function (ev) {
            if (this._is_valid_barcode_model) {
                if (this._controller_base) {
                    ev.stopPropagation();
                    this._controller_base._onDocumentKeyDown(ev);
                }
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});
