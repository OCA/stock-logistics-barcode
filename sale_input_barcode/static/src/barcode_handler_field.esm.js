import {Component, usePlugin, useProps, xml} from "@odoo/owl";
import {BarcodePlugin} from "@barcodes/barcode_plugin";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useBus} from "@web/core/utils/hooks";

/**
 * Replaces the `barcode_handler` widget removed in Odoo 20.0: writes each
 * scanned barcode in the field, which triggers its onchange.
 */
export class SaleBarcodeHandlerField extends Component {
    static template = xml``;
    props = useProps({...standardFieldProps});

    setup() {
        const barcode = usePlugin(BarcodePlugin);
        useBus(barcode.bus, "barcode_scanned", (ev) =>
            this.props.record.update({[this.props.name]: ev.detail.barcode})
        );
    }
}

registry.category("fields").add("sale_barcode_handler", {
    component: SaleBarcodeHandlerField,
});
