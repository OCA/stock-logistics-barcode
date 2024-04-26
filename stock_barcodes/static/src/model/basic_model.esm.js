odoo.define("stock_barcodes.BasicModel", function (require) {
    var BasicModel = require("web.BasicModel");

    BasicModel.include({
        _readMissingFields: function (list, resIDs, fieldNames) {
            // This allows for "static list" (x2many fields) to always update there
            // fields
            if (list.getContext().always_reload) {
                for (const key in list._cache) {
                    delete list._cache[key];
                }
            }
            return this._super.apply(this, [list, resIDs, fieldNames]);
        },
    });
});
