/* Copyright 2024 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define(
    "stock_barcodes_picking_batch_revision.boolean_toggle_big",
    function (require) {
        "use strict";

        var basic_fields = require("web.basic_fields");
        var field_registry = require("web.field_registry");

        var FieldBarcodeBooleanToggleBig = basic_fields.BooleanToggle.extend({
            /**
             * Add class o_boolean_toggle_big to be able to modify css
             *
             * @override
             * @private
             */
            _render: function () {
                this._super.apply(this, arguments);
                this.$el.addClass("o_boolean_toggle_big");
            },
        });

        field_registry.add("boolean_toggle_big", FieldBarcodeBooleanToggleBig);
    }
);
