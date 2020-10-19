/* Copyright 2020 Sunflower IT
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('barcodes_multiline.BarcodeEvents', function (require) {
    'use strict';

    var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents;

    // Not any character signifies 'end of barcode' anymore;
    // barcode only ends when 50ms have passed without input.
    BarcodeEvents.suffix = /$^/;

    // Barcodes are 3 characters minimum and may contain newline characters
    BarcodeEvents.regexp = /([\s\S]{3,})/;
});
