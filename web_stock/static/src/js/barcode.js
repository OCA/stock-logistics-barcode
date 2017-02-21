/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('web_stock.barcode', function(require) {
    'use strict';

    var snippet_animation = require('web_editor.snippets.animation');
    var ParentedMixin = require('web.mixins').ParentedMixin;
    var BarcodeHandlerMixin = require('barcodes.BarcodeHandlerMixin');
    var BarcodeParser = require('barcodes.BarcodeParser');
    var Model = require('web.DataModel');
    
    var core = require('web.core');
    var _t = core._t;

    snippet_animation.registry.js_picking_form_barcode = snippet_animation.Class.extend(ParentedMixin, BarcodeHandlerMixin, {
        
        selector: '.js_picking_form_barcode',
        loaded: false,
        barcodeParser: false,
        barcodeHistory: [],  // Most recent first
        
        // Let subclasses add custom behavior before onchange. Must return a deferred.
        // Resolve the deferred with true proceed with the onchange, false to prevent it.
        preOnchangeHook: function() {
            return $.Deferred().resolve(this.loaded);
        },
    
        start: function() {
            this._super.apply(this, arguments);
            // Compat w/ multi-barcodes update
            this.el = this.$target[0];
            this.actionMap = {
                'product': this.handleProductScan,
                'error': this.throwError,
                'lot': this.handleLotScan,
            };
            if (!this.barcodeParser) {
                var nomenclatureId = $('#barcodeNomenclatureId').val();
                if (!nomenclatureId) {
                    return;
                }
                this.barcodeParser = new BarcodeParser({
                    'nomenclature_id': [nomenclatureId],
                });
                this.barcodeParser.load().then(this.onParserLoad);
            }
            this.$target.on('barcode_scanned', this.on_barcode_scanned);
        },

        onParserLoad: function() {
            this.loaded = true;
            console.log('Barcode parser initialized');
        }

        on_barcode_scanned: function(barcode) {
            console.log(barcode);
            var self = this;
            // Call hook method possibly implemented by subclass
            this.preOnchangeHook(barcode).then(function(proceed) {
                if (proceed === true) {
                    var parsedBarcode = self.barcodeParser.parse_barcode(barcode);
                    self.barcodeHistory.unshift(parsedBarcode);
                    try{
                        self.actionMap[parsedBarcode.type].call(self, parsedBarcode);
                    } catch (err) {
                        self.actionMap.error.call(self, parsedBarcode, err);
                    }
                }
            });
        },
        
        throwError: function(parsedBarcode, exception) {
            console.log('throwError called with');
            console.log(parsedBarcode);
            console.log(exception);
            // @TODO: create throwError method
        },
        
        handleProductScan: function(parsedBarcode) {
            var barcodeQty = parseFloat(parsedBarcode.value);
            if (barcodeQty === 0.0) {
                barcodeQty = 1.0;
            }
            var productCode = this._stripBarcodePrefix(parsedBarcode);
            var $productEls = $('.js-picking-picked-qty[data-barcode="' + productCode.code + '"]');
            if ($productEls.length === 0) {
                alert(_t('No product on page matching barcode ') +
                      ' "' + parsedBarcode.code + '"');
                return;
            }
            this._handleBarcodeQty(barcodeQty, $productEls);
        },
        
        handleLotScan: function(parsedBarcode) {
            var self = this;
            var lotObj = new Model('stock.production.lot');
            var barcodeQty = parseFloat(parsedBarcode.value);
            if (barcodeQty === 0.0) {
                barcodeQty = 1.0;
            }
            var lotCode = this._stripBarcodePrefix(parsedBarcode);
            lotObj.query(['name', 'product_id'])
                .filter(['|',
                         ['name', '=', lotCode.code],
                         ['ref', '=', lotCode.code],
                        ])
                .limit(1)
                .first()
                .then(function(lot){
                    var $productEls = $('.js-picking-picked-qty[data-product-id="' + lot.product_id[0] + '"]');
                    if ($productEls.length === 0) {
                        alert(_t('No product on page matching barcode') +
                              ' "' + lotCode.code + '"');
                        return;
                    }
                    self._handleBarcodeQty(barcodeQty, $productEls);
                });
        },
        
        _handleBarcodeQty: function(barcodeQty, $productEls) {
            _.each($productEls, function(el){
                var $el = $(el);
                // @TODO: Add better logic here
                var maxVal = parseFloat($el.data('product-qty'));
                var existingVal = parseFloat($el.val());
                if (isNaN(existingVal)) {
                    existingVal = 0.0;
                }
                if (barcodeQty !== 0.0) {
                    var newVal = barcodeQty + existingVal;
                    if (newVal > maxVal) {
                        newVal = maxVal;
                        barcodeQty -= maxVal - existingVal;
                    } else if (newVal < 0) {
                        barcodeQty = newVal;
                        newVal = 0;
                    } else {
                        barcodeQty -= newVal - existingVal;
                    }
                    $el.val(newVal);
                }
            });
        },
        
        /* It identifies difference of code + base_code, and provides
         * the prefix + a version of the code with the prefix and
         * zeroes that were appended by parser removed
         *
         *  Given:
         *      {encoding: "any", type: "product", code: "11023454545656767", base_code: "11000004545656767", value: 23.45}
         *  For Nomenclature:
         *      Product: 11{NNNDD}
         *  Get:
         *      {prefix: "110", code: "4545656767"}
         *      
         **/
        _stripBarcodePrefix: function(parsedBarcode) {
            var baseCode = parsedBarcode.base_code.split(""),
                unmatched = 0,
                leftCode = [],
                rightCode = [];
            _.each(parsedBarcode.code.split(""), function(chr, idx) {
                if (chr != baseCode[idx]) {
                    unmatched += 1;
                }
                if (!unmatched) {
                    leftCode.push(baseCode[idx]);
                } else {
                    rightCode.push(baseCode[idx]);
                }
            });
            leftCode = leftCode.join("");
            rightCode = rightCode.join("").substring(unmatched);
            var prefix, code;
            if (rightCode.length === 0) {
                prefix = '';
                code = leftCode;
            } else {
                prefix = leftCode;
                code = rightCode;
            }
            return {prefix: prefix, code: code};
        },
        
    });
    
    return {
        BarcodeForm: snippet_animation.registry.js_picking_form_barcode,
    };
    
});
