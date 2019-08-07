/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('stock_barcodes.FieldFloatNumericMode', function(require) {
    'use strict';

    var basic_fields = require('web.basic_fields');
    var field_registry = require('web.field_registry');

    var FieldFloatNumericMode = basic_fields.FieldFloat.extend({
        events: _.extend({}, basic_fields.FieldFloat.prototype.events, {
            "focusin": "_onFocusIn",
        }),
        _onFocusIn: function () {
            // Auto select all content when user enters into fields with this
            // widget.
            this.$input.select();
        },
        _prepareInput: function ($input) {
            // Set numeric mode to display numeric keyboard in mobile devices
            var $input_numeric = this._super($input);
            $input_numeric.attr({'inputmode': 'numeric'});
            return $input_numeric;
        },
    });
    field_registry.add('FieldFloatNumericMode', FieldFloatNumericMode);
    return FieldFloatNumericMode;
});
