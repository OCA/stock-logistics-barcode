/*
Copyright (C) 2017-Today GRAP (http://www.grap.coop)
@author: Sylvain LE GAL (https://twitter.com/legalsylvain)
License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define('barcodes_search.systray', function (require) {
    "use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    // Menu item appended in the systray part of the navbar
    // On click : Display a barcode search form view
    var BarcodeSearchItem = Widget.extend({
        template:'barcodes_search.BarcodeSearchItem',
        events: {
            "click": "onClick",
        },

        onClick: function (event) {
            event.preventDefault();
            return this.do_action('barcodes_search.action_barcode_search_form');
        },

    });

    SystrayMenu.Items.push(BarcodeSearchItem);

});
