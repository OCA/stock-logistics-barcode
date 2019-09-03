/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('stock_barcodes.FormController', function (require) {
    'use strict';

    var FormController = require('web.FormController');

    FormController.include({
        _barcodeScanned: function (barcode, target) {
            var self = this;
            /*
            Set control focus to package_qty or product_qty directly after
            scan a barcode for manual entry mode entries.
            */
            this._super(barcode, target).then(function () {
                var manual_entry_mode = self.$("div[name='manual_entry'] input").val();
                if (manual_entry_mode) {
                    var packaging = self.$("div[name='packaging_id'] input").val();
                    if (packaging) {
                        self.$("input[name='packaging_qty']").focus();
                    } else {
                        self.$("input[name='product_qty']").focus();
                    }
                }
            });
        },
        renderButtons: function ($node) {
            /*
            Hide save and discard buttons from wizard, for this form do
            anything and confuse the user if he wants do a manual entry. All
            extended models from  wiz.stock.barcodes.read do not have this
            buttons.
            */
            this._super($node);
            if (this.modelName.includes('wiz.stock.barcodes.read.')) {
                this.$buttons.find('.o_form_buttons_edit')
                    .css({'display': 'none'});
            }
        },
        canBeDiscarded: function (recordID) {
            /*
             Silent the warning that says that the record has been modified.
             */
            if (!this.modelName.includes('wiz.stock.barcodes.read.')) {
                return this._super.apply(this, arguments);
            }
            return $.when(false);
        },
    });
});
