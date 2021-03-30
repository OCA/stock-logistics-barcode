/* Copyright 2021 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("stock_barcodes.FormView", function(require) {
    "use strict";

    var FormView = require("web.FormView");

    FormView.include({
        /**
         * Adds support to define the 'control_panel_hidden' context key to
         * override 'withControlPanel' option.
         *
         * @override
         */
        _extractParamsFromAction: function(action) {
            const params = this._super.apply(this, arguments);
            if (action && action.context && action.context.control_panel_hidden) {
                params.withControlPanel = false;
            }
            return params;
        },
    });
});
