odoo.define('web.FormViewBarcode', function (require) {
    "use strict";

    var FormView = require('web.FormView');

    var FormViewBarcode = FormView.include({
        // This is needed, otherwise when scanning a barcode for an Inventory Adjustment instead of triggering the
        // python function on_barcode_scanned, it will focus on the manual entry data boolean field and do nothing
        defaults: _.extend({}, FormView.prototype.defaults, {
            disable_autofocus: true,
        }),
        on_attach_callback: function () {
            /*
            This is needed because, whenever we click the checkbox to enter data manually, the checkbox will be
            focused causing that when we scan the barcode afterwards, it will not perform the python on_barcode_scanned
            function.
            */
            var self = this;
            return $.when(this._super()).then(function () {
                var checkbox = $("input[name='manual_entry']");
                if (checkbox) {
                    $(checkbox).on('click', function (event) {
                        $(checkbox).blur();
                    });
                }
                // This is an ugly fix in order to keep the product when the user removes last scanned log
                $(".extra_product").css('display', 'none')
                // Add class that will set overflow: inherit in order to keep responsive view even when button has been clicked
                if (self.model.includes("wiz.stock.barcodes.read.")) {
                    $(".o_main").addClass("overflow_inherit");
                    $(".o_main_content").addClass("overflow_inherit");
                    $(".breadcrumb").addClass("breadcrumb_full");
                    $(".o_cp_right").hide();
                }
                else {
                    $(".o_main").removeClass("overflow_inherit");
                    $(".o_main_content").removeClass("overflow_inherit");
                    $(".breadcrumb").removeClass("breadcrumb_full");
                    $(".o_cp_right").show();
                }
            });
        },
        on_processed_onchange: function (result) {
            /*
            Needed in order to change the class of the div that displays the message. In v10 cannot set same field
            multiple times in form view since it will not show the proper value. It has to be done through js if we do
            not want to define multiple message fields
            */
            this._super.apply(this, arguments);
            if (result && result.value) {
                this._setAlert(result.value.message_type);
            }
            if (this.model.includes("wiz.stock.barcodes.read.")) {
                $("input").blur()
            }
        },
        toggle_buttons: function() {
            /*
            Hide save and discard buttons from wizard, for this form do
            anything and confuse the user if he wants do a manual entry. All
            extended models from  wiz.stock.barcodes.read do not have this
            buttons.
            */
            this._super.apply(this, arguments);
            if (this.model.includes('wiz.stock.barcodes.read.')){
                this.$buttons.find('.o_form_buttons_edit').toggle(false);
            }
        },
        can_be_discarded: function (message) {
            /*
            This prevents the dialog box telling the user that changes have been made whenever we exit the form view
            */
            if (!this.model.includes("wiz.stock.barcodes.read.")) {
                return this._super(message);
            }
            return $.when(false);
        },
        _setAlert: function (message_type) {
            var div = $('#alert');
            if (message_type) {
                $(div).removeClass();
                $(div).addClass('alert');
                switch (message_type) {
                    case 'success':
                        $(div).addClass('alert-success');
                        break;
                    case 'info':
                        $(div).addClass('alert-info');
                        break;
                    case 'not_found':
                    case 'more_match':
                        $(div).addClass('alert-danger');
                        break;
                }
            }
        },
    });

    return FormViewBarcode;

});