/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("stock_barcodes.FieldFloatNumericMode", function(require) {
    "use strict";

    var basic_fields = require("web.basic_fields");
    var field_registry = require("web.field_registry");

    var FieldFloatNumericMode = basic_fields.FieldFloat.extend({
        events: _.extend({}, basic_fields.FieldFloat.prototype.events, {
            focusin: "_onFocusIn",
        }),
        _onFocusIn: function() {
            // Auto select all content when user enters into fields with this
            // widget.
            this.$input.select();
        },
        _prepareInput: function($input) {
            // Set numeric mode to display numeric keyboard in mobile devices
            var $input_numeric = this._super($input);
            $input_numeric.attr({inputmode: "numeric"});
            return $input_numeric;
        },
    });

    var FieldBarcodeBooleanToggle = basic_fields.BooleanToggle.extend({
        /*
        This is needed because, whenever we click the checkbox to enter data
        manually, the checkbox will be focused causing that when we scan the
        barcode afterwards, it will not perform the python on_barcode_scanned
        function.
        */
        _onClick: function(event) {
            this._super(event);
            //            This.getFocusableElement().blur();
            //            HACK: Fails normal way
            _.defer(() => {
                this.getFocusableElement().blur();
            });
        },

        _render: function() {
            this._super.apply(this, arguments);
            const accesskey = this.attrs && this.attrs.accesskey;
            if (accesskey) {
                this.$el.attr("accesskey", accesskey);
            }
        },
    });

    field_registry.add("FieldFloatNumericMode", FieldFloatNumericMode);
    field_registry.add("FieldBarcodeBooleanToggle", FieldBarcodeBooleanToggle);

    return {
        FieldFloatNumericMode: FieldFloatNumericMode,
        FieldBarcodeBooleanToggle: FieldBarcodeBooleanToggle,
    };
});
