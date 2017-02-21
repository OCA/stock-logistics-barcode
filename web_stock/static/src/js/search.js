/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('web_stock.search', function(require) {
    'use strict';

    var snippet_animation = require('web_editor.snippets.animation');

    /* It provides Stock Picking search form and event handlers
     **/
    snippet_animation.registry.js_picking_search = snippet_animation.Class.extend({
        
        selector: '.js_picking_search',
        
        start: function() {
            var self = this;
            this.$target.find('.js_picking_submit_immediate').change(function() {
                self.$target.submit();
            });
        },
        
    });
    
    return {
        PickingSearch: snippet_animation.registry.js_picking_search,
    };
    
});
