/* Copyright 2016 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

// Most of this code is bad and I feel bad. Rewrite once I know it will work

odoo.define('web_stock.tour', function(require) {
    'use strict';

    var Core = require('web.core');
    var Tour = require('web.Tour');
    var _t = Core._t;
    
    Tour.register({
        id: "test_web_stock",
        name: _t("Test web_stock things"),
        
    });
    
});
