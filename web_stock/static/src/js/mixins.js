/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('web_stock.mixins', function(require) {
    'use strict';
    
    /* It should provide a more basic version of website_form js
     * This allows for removal of website dependencies
     **/
    var formMixin = {
        handleSubmit: function(event) {
            var self = this;
            event.preventDefault();
            var $target = $(event.target);
            var data = $target.serializeArray();
            return $.ajax({
                method: $target.attr('method') || 'GET',
                url: $target.attr('action'),
                data: data,
                dataType: 'json',
            }).done(function(data) {
                if(data.errors.length || data.error_fields.length) {
                    // @TODO: Handle error fields
                    var $errorDivs = $('');
                    _.each(data.errors, function(error) {
                        $errorDivs.append('<div class="alert">' + error + '</div>');
                    });
                    self.$target.find('.js_picking_form_result').html($errorDivs);
                } else {
                    var redirectUri = self.$target.data('success-page');
                    if (redirectUri) {
                        window.location.href = redirectUri;
                    } else {
                        window.location.reload();
                    }
                }
            });
        }
    };

    var pickingDialogMixin = {
        init: function(parent) {
            this._super(parent, this.options);
        },
    };
    
    return {
        formMixin: formMixin,
        pickingDialogMixin: pickingDialogMixin,
    };
    
});
