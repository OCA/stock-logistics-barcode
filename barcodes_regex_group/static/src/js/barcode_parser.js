odoo.define('barcodes_regex_group.BarcodeParser', function (require) {
    "use strict";

    var BarcodeParser = require('barcodes.BarcodeParser');

    BarcodeParser.include({
        init: function(attributes) {
            return this._super(attributes);
        },

        match_pattern: function(barcode, pattern, encoding) {
            var match = this._super(barcode, pattern, encoding);

            // Abuse 'value' to store the result, since it goes to 'parsed_result'
            if ((match.match != null) && (match.match.length > 1))
                match.value = match;
            return match;
        },

        parse_barcode: function(barcode) {
            // TODO: filter rules by their applicability to the currently active model
            // model = self.env.cache['_barcode_active_model']
            // if model:
            //     rule_ids_filtered = this.rule_ids.filtered(
            //         lambda r: (not r.model_ids)
            //         or model in r.model_ids.mapped('model')).ids
            //     rule_ids_backup = this._cache['rule_ids']
            //    this._cache['rule_ids'] = rule_ids_filtered

            var parsed_result = this._super(barcode);

            // TODO: restore rule_ids
            // if model:
            //    this._cache['rule_ids'] = rule_ids_backup

            // Post-process any result of group-matching
            if (parsed_result.value.match !== undefined) {
                var match = parsed_result.value;
                parsed_result.value = 0;
                parsed_result.code = match.match[1];
            }

            return parsed_result;
        }
    });

});
