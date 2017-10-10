/* Copyright 2016-2017 LasLabs Inc.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define_section('base_gtin', ['barcodes.BarcodeParser'], function(test) {
    "use strict";
    
    var EAN14_VALID = [
        '12345678911230',
        '12345278911333',
        '56734527891139',
    ];


    var EAN14_INVALID = [
        '12335678911230',
        '56734527891131',
        'abcsdeferfrfgr',
        '2345658911239',
    ];
    
    test('It should return proper checksum for EAN-14',
        function(assert, BarcodeParser) {
            var eans = EAN14_VALID,
                barcode_parser = new BarcodeParser({
                    nomenclature_id: 1,
                });
            for(var i=0, l=eans.length; i < l; i ++) {
                var ean = eans[i];
                strictEqual(
                    barcode_parser.ean14_checksum(ean),
                    parseInt(ean.slice(-1))
                );
            }
        }
    );
    
    test('It should return -1 checksum for EAN-14',
        function(assert, BarcodeParser) {
            var eans = EAN14_INVALID,
                barcode_parser = new BarcodeParser({
                    nomenclature_id: 1,
                });
            for(var i=0, l=eans.length; i < l; i ++) {
                var ean = eans[i];
                notEqual(
                    barcode_parser.ean14_checksum(ean),
                    parseInt(ean.slice(-1))
                );
            }
        }
    );
    
    test('It should properly identify valid EAN-14',
        function(assert, BarcodeParser) {
            var eans = EAN14_VALID,
                barcode_parser = new BarcodeParser({
                    nomenclature_id: 1,
                });
            for(var i=0, l=eans.length; i < l; i ++) {
                var ean = eans[i];
                strictEqual(
                    barcode_parser.check_encoding(ean, 'ean14'),
                    true
                );
            }
        }
    );
    
    test('It should properly identify valid EAN-14',
        function(assert, BarcodeParser) {
            var eans = EAN14_INVALID,
                barcode_parser = new BarcodeParser({
                    nomenclature_id: 1,
                });
            for(var i=0, l=eans.length; i < l; i ++) {
                var ean = eans[i];
                strictEqual(
                    barcode_parser.check_encoding(ean, 'ean14'),
                    false
                );
            }
        }
    );
    
    test('It should return result of super',
        function(assert, BarcodeParser) {
            var barcode_parser = new BarcodeParser({
                    nomenclature_id: 1,
                });
            strictEqual(
                barcode_parser.check_encoding('1234', 'any'),
                true
            );
        }
    );

});
