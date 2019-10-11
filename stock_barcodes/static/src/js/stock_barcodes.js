/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('stock_barcodes.FormViewBarcodeHandler', function(require) {
    'use strict';

    var FormViewBarcodeHandler = require('barcodes.FormViewBarcodeHandler');

    FormViewBarcodeHandler.include({
        on_barcode_scanned: function (barcode) {
            var self = this;
            /*
            Set control focus to package_qty or product_qty directly after
            scan a barcode for manual entry mode entries.
            */
            this._super(barcode);
            var manual_entry_mode = self.$("div[name='manual_entry'] input").val();
            if (manual_entry_mode){
                var packaging = self.$("div[name='packaging_id'] input").val();
                if (packaging) {
                    self.$("input[name='packaging_qty']").focus();
                } else {
                    self.$("input[name='product_qty']").focus();
                };
            };
        },
    });
});
