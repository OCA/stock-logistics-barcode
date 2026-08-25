import {patch} from "@web/core/utils/patch";
import {useEffect} from "@odoo/owl";
import {FormController} from "@web/views/form/form_controller";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {ListController} from "@web/views/list/list_controller";
import {isAllowedBarcodeModel} from "../../utils/barcodes_models_utils.esm";

/* Guarda las referencias originales ANTES del patch */
const _origFormSetup = FormController.prototype.setup;
const _origKanbanSetup = KanbanController.prototype.setup;
const _origListSetup = ListController.prototype.setup;

function setupViewHotkeys() {
    // Tu lógica (listeners, overlays, etc.)
    useEffect(
        () => {
            // Attach...
            return () => {
                // Cleanup...
            };
        },
        () => []
    );
}

patch(FormController.prototype, {
    setup() {
        if (typeof _origFormSetup === "function") {
            _origFormSetup.call(this, ...arguments);
        }
        if (isAllowedBarcodeModel(this.props.resModel)) {
            setupViewHotkeys.call(this);
        }
    },
});

patch(KanbanController.prototype, {
    setup() {
        if (typeof _origKanbanSetup === "function") {
            _origKanbanSetup.call(this, ...arguments);
        }
        if (isAllowedBarcodeModel(this.props.resModel)) {
            setupViewHotkeys.call(this);
        }
    },
});

patch(ListController.prototype, {
    setup() {
        if (typeof _origListSetup === "function") {
            _origListSetup.call(this, ...arguments);
        }
        if (isAllowedBarcodeModel(this.props.resModel)) {
            setupViewHotkeys.call(this);
        }
    },
});
