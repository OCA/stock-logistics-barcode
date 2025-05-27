/** @odoo-module */

import {onWillStart, useState} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {SignatureWidget} from "@web/views/widgets/signature/signature";
import {patch} from "@web/core/utils/patch";

const _extractProps = SignatureWidget.extractProps;
SignatureWidget.extractProps = ({attrs, field}) => {
    return Object.assign(_extractProps({attrs, field}), {
        addClassName: attrs.addClassName,
        labelClassName: attrs.labelClassName,
        barcodeView: Boolean(attrs.barcodeView),
    });
};

SignatureWidget.props = {
    ...SignatureWidget.props,
    addClassName: {type: String, optional: true, default: ""},
    labelClassName: {type: String, optional: true, default: ""},
    barcodeView: {type: Boolean, optional: true, default: false},
};

patch(SignatureWidget.prototype, "stock_barcodes_quality_control.SignatureWidget", {
    setup() {
        this._super();
        this.orm = useService("orm");
        this.state = useState({
            countSignDelivery: "",
        });
        onWillStart(async () => {
            if (
                this.env.searchModel.resModel === "wiz.stock.barcodes.read.picking" &&
                this.props.barcodeView
            ) {
                this.getCountsSignDelivery();
            }
        });
        useBus(this.env.bus, "STOCK_BARCODES:SIGN-UPDATED", () => {
            this.getCountsSignDelivery();
        });
    },

    async getCountsSignDelivery() {
        const active_id = this.env.searchModel._context.active_id;
        const counts = await this.orm.call(
            "stock.picking",
            "get_count_sign_delivery_slip",
            [active_id]
        );
        this.state.countSignDelivery = counts > 0 ? `(${counts})` : "";
    },
});
