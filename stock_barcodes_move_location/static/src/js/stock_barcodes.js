/* Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("stock_barcodes_move_location.FormController", function(require) {
    "use strict";

    var FormController = require("web.FormController");

    FormController.include({
        canBeDiscarded: function(recordID) {
            /*
            This prevents the dialog box telling the user that changes have been made whenever we exit the form view
            */
            if (!this.modelName.includes("wiz.stock.barcodes.read.move.location")) {
                return this._super(recordID);
            }
            return $.when(false);
        },
    });
});
