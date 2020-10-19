odoo.define('barcodes_multiline.tour', function (require) {
    "use strict";

    var core = require('web.core');
    var tour = require('web_tour.tour');

    var _t = core._t;

    tour.register(
        'barcodes_multiline.tour',
        {
            url: "/web",
        },
        [
            tour.STEPS.MENU_MORE,
            {
                content: _t("Go to Settings."),
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"], ' +
                         '.oe_menu_toggler[data-menu-xmlid="base.menu_administration"]',
                position: "bottom",
            },
            {
                content: _t("Edit barcode-sensitive Odoo record."),
                trigger: '.oe_menu_leaf[data-menu-xmlid="barcodes_multiline.demo_matrix_menu"]',
                extra_trigger: '.o_web_settings_dashboard',
                position: "bottom",
            },
            {
                content: _t("Simulate the scanning of a multiline barcode"),
                trigger: ".o_form_textarea[name='text']",
                extra_trigger: '.o_form_editable',
                run: function () {
                    var a = 'AAAAA\nBBBBB\nCCCCC';
                    for (var i=0; i<a.length; i++) {
                        var e = new Event('keypress');
                        e.which = a[i].charCodeAt(0);
                        document.getElementsByTagName('body')[0].dispatchEvent(e);
                    }
                    // Hack to wait for 200 ms before entering next step
                    _.delay(function () {
                        $(".o_form_textarea[name='text']").addClass('ready');
                    }, 200);
                },
            },
            {
                content: _t("Save record"),
                extra_trigger: ".o_form_textarea.ready[name='text']",
                trigger: '.o_form_button_save',
            },
            {
                content: _t("Content has multiple lines"),
                trigger: "span.o_form_textarea:contains('CCCCC')",
            },
        ]
    );

});
