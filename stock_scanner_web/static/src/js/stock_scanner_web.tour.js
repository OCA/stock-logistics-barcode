/* © 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
   © 2017 Angel Moya <angel.moya@pesol.es>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("stock_scanner_web.tour", function (require) {
    "use strict";

    var Tour = require("web.Tour");


    Tour.register({
        id: "stock_scanner_web",
        name: "Stock Scanner Web test",
        path: "/stock_scanner_web",
        mode: "test",
        steps: [
          {
              title: "Click Tutorial",
              element: "a:contains('Tutorial')",
              waitFor: "a:contains('Tutorial')"
          },
          {
              title: "Click Step types",
              element: "a:contains('Step types')",
              waitFor: "a:contains('Step types')"
          },
          {
              title: "Click Go",
              element: "#btn-go",
              waitFor: "#btn-go"
          },
          {
              title: "Click Go",
              element: "#btn-go",
              waitFor: "#btn-go"
          },
          {
              title: "Click Go to Error step",
              element: ".js_item:contains('Go to Error step')",
              waitFor: ".js_item:contains('Go to Error step')"
          },
          {
              title: "Click Back",
              element: "#btn-back",
              waitFor: "#btn-back"
          },
          {
              title: "Click Go to next step",
              element: "a:contains('Go to next step')",
              waitFor: "a:contains('Go to next step')"
          },
          {
              title: "Click Yes",
              element: "#btn-yes",
              waitFor: "#btn-yes"
          },
          {
              title: "Click Submit",
              element: ".btn-primary",
              waitFor: ".btn-primary"
          },
          {
              title: "Click Submit",
              element: ".btn-primary",
              waitFor: ".btn-primary"
          },
          {
              title: "Click Submit",
              element: ".btn-primary",
              waitFor: ".btn-primary"
          },
          {
              title: "Click Back",
              element: "#btn-back",
              waitFor: "#btn-back"
          },
          {
              title: "Click Tutorial",
              element: "a:contains('Tutorial')",
              waitFor: "a:contains('Tutorial')"
          },
          {
              title: "Stock Scanner Web Type",
              element: "a:contains('Stock Scanner Web Type')",
              waitFor: "a:contains('Stock Scanner Web Type')"
          }
        ]
    });
});
