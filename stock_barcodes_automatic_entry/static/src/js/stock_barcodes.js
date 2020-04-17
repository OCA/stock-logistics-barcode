/* Copyright 2019 Eficent Business and IT Consulting Services S.L.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("stock_barcodes_automatic_entry.FormController", function(require) {
    "use strict";

    var FormController = require("web.FormController");

    FormController.include({
        _barcodeActiveScanned: function() {
            return this._super.apply(this, arguments).then(function() {
                if ($(".barcode-automatic-entry")) {
                    $(".barcode-automatic-entry").trigger("click");
                }
            });
        },
    });
});
