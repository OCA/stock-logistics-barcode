/* Copyright 2022 Tecnativa - Sergio Teruel
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("stock_barcodes_picking_batch.BarcodesModelsMixin", function(require) {
    "use strict";

    const BarcodesModelsMixin = require("stock_barcodes.BarcodesModelsMixin");

    var _barcode_models_picking_batch = [
        "stock.picking.batch",
        "wiz.candidate.picking.batch",
    ];
    BarcodesModelsMixin._barcode_models.push.apply(
        BarcodesModelsMixin._barcode_models,
        _barcode_models_picking_batch
    );
});
