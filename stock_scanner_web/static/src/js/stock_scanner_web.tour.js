/* © 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
   © 2017 Angel Moya <angel.moya@pesol.es>
   © 2020 Eric Antones <eantones@nuobit.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("stock_scanner_web.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "stock_scanner_web_tour",
        {
            url: "/stock_scanner_web",
            test: true,
        },
        [
            {
                content: 'click on tutorial',
                extra_trigger: "div:has(.container:has(h2:containsExact('Main Menu')):has(a:contains('Tutorial')))",
                trigger: "a:contains('Tutorial')",
            },
            {
                content: 'click on step types',
                extra_trigger: "div:has(.container:has(h2:containsExact('Tutorial')):has(a:contains('Step types')))",
                trigger: "a:contains('Step types')",
            },
            {
                content: "Click Go",
                extra_trigger: "div:has(.container:has(h2:containsExact('Introduction')):has(p:containsExact('Welcome on the stock_scanner module.')):has(a[id='btn-go']:containsExact('Go')))",
                trigger: "#btn-go",
            },
            {
                content: "Click Go",
                extra_trigger: "div:has(.container:has(h2:containsExact('Message step')):has(a[id='btn-go']:containsExact('Go')))",
                trigger: "#btn-go",
            },
            {
                content: "Click Go to Error step",
                extra_trigger: "a:contains('Go to Error step')",
                trigger: "a:contains('Go to Error step')",
            },
            {
                content: "Click Back",
                extra_trigger: "div:has(.container:has(h2:containsExact('Error step')):has(a[id='btn-back']:containsExact('Back')))",
                trigger: "#btn-back",
            },
            {
                content: "Click Go to next step",
                extra_trigger: "div:has(.container:has(h2:containsExact('Main Menu')):has(a:contains('Go to next step')))",
                trigger: "a:contains('Go to next step')",
            },
            {
                content: "Click Yes",
                extra_trigger: "div:has(.container:has(h2:containsExact('Confirm step')):has(a[id='btn-yes']:containsExact('Yes')))",
                trigger: "#btn-yes",
            },
            {
                content: "Click Submit",
                extra_trigger: "div:has(.container:has(h2:containsExact('Number (integer) step')):has(.btn-primary:containsExact('Submit')))",
                trigger: ".btn-primary:containsExact('Submit')",
            },
            {
                content: "Click Submit",
                extra_trigger: "div:has(.container:has(h2:containsExact('Quantity (float) step')):has(.btn-primary:containsExact('Submit')))",
                trigger: ".btn-primary:containsExact('Submit')",
            },
            {
                content: "Click Submit",
                extra_trigger: "div:has(.container:has(h2:containsExact('Text input step')):has(.btn-primary:containsExact('Submit')))",
                trigger: ".btn-primary:containsExact('Submit')",
            },
            {
                content: "Click Go to menu",
                extra_trigger: "div:has(.container:has(h2:containsExact('Final step')):has(p:containsExact('After this step, the scenario is finished.')):has(a[id='btn-back']:containsExact('Go to menu')))",
                trigger: "#btn-back",
            },
            {
                content: "Click Tutorial",
                extra_trigger: "div:has(.container:has(h2:containsExact('Main Menu')):has(a:contains('Tutorial')))",
                trigger: "a:contains('Tutorial')",
            },
            {
                content: "Stock Scanner Web Type",
                extra_trigger: "div:has(.container:has(h2:containsExact('Tutorial')):has(a:contains('Stock Scanner Web Type')))",
                trigger: "a:contains('Stock Scanner Web Type')",
            }
        ]
    );
});
