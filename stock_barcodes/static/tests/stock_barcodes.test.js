import {afterEach, expect, test} from "@odoo/hoot";
import {BarcodeHandlerField} from "@barcodes/barcode_handler_field";
import {StockBarcodesMainMenu} from "../src/views/actions/stock_barcode_main_menu.esm";
import {isAllowedBarcodeModel} from "../src/utils/barcodes_models_utils.esm";
import {isStockBarcodesReader} from "../src/utils/barcode_handler_field.esm";
import {showQuantOperations} from "../src/views/kanban/kanban_quant_operations.esm";
import {waitVisibleElement} from "../src/utils/wait_visible_elment_helper.esm";

test.tags("headless");

afterEach(() => {
    document.body.replaceChildren();
});

test("barcode models are restricted to supported models", () => {
    expect(isAllowedBarcodeModel("stock.picking")).toBe(true);
    expect(isAllowedBarcodeModel("wiz.stock.barcodes.read.picking")).toBe(true);
    expect(isAllowedBarcodeModel("res.partner")).toBe(false);
});

test("waitVisibleElement resolves an existing visible element", async () => {
    const element = document.createElement("input");
    element.className = "barcode-test-input";
    element.getBoundingClientRect = () => ({
        width: 10,
        height: 10,
        top: 0,
        right: 10,
        bottom: 10,
        left: 0,
    });
    document.body.appendChild(element);

    const result = await waitVisibleElement(".barcode-test-input", 50);

    expect(result).toBe(element);
});

test("main menu sends scanned barcode to the barcode wizard", async () => {
    const calls = [];
    const mainMenu = {
        ormService: {
            call: async (...args) => {
                calls.push(args);
            },
        },
    };

    await StockBarcodesMainMenu.prototype._onBarcodeScanned.call(
        mainMenu,
        "0123456789012"
    );

    expect(calls).toEqual([
        ["wiz.stock.barcodes.read", "process_barcode", [[], "0123456789012"]],
    ]);
});

function addScanButton(steps) {
    const button = document.createElement("button");
    button.id = "dummy_on_barcode_scanned";
    button.addEventListener("click", () => steps.push("click"));
    document.body.appendChild(button);
}

function makeBarcodeField(resModel, name, update) {
    return {props: {name, record: {resModel, update}}};
}

test("barcode reader is restricted to the scan wizards _barcode_scanned", () => {
    const reader = makeBarcodeField(
        "wiz.stock.barcodes.read.picking",
        "_barcode_scanned"
    );
    expect(isStockBarcodesReader(reader.props)).toBe(true);
    const otherField = makeBarcodeField("wiz.stock.barcodes.read.picking", "barcode");
    expect(isStockBarcodesReader(otherField.props)).toBe(false);
    const otherModel = makeBarcodeField("stock.picking", "_barcode_scanned");
    expect(isStockBarcodesReader(otherModel.props)).toBe(false);
});

test("barcode reader waits for the record update before scanning", async () => {
    const steps = [];
    let resolveUpdate = null;
    addScanButton(steps);
    const field = makeBarcodeField(
        "wiz.stock.barcodes.read.picking",
        "_barcode_scanned",
        (values) => {
            steps.push(values);
            return new Promise((resolve) => {
                resolveUpdate = resolve;
            });
        }
    );

    const scan = BarcodeHandlerField.prototype.onBarcodeScanned.call(field, {
        detail: {barcode: "0123456789012"},
    });
    expect(steps).toEqual([{_barcode_scanned: "0123456789012"}]);

    resolveUpdate();
    await scan;
    expect(steps).toEqual([{_barcode_scanned: "0123456789012"}, "click"]);
});

test("barcode handler keeps the core behaviour outside the scan wizards", async () => {
    const steps = [];
    addScanButton(steps);
    const field = makeBarcodeField("stock.picking", "_barcode_scanned", (values) => {
        steps.push(values);
    });

    await BarcodeHandlerField.prototype.onBarcodeScanned.call(field, {
        detail: {barcode: "0123456789012"},
    });

    expect(steps).toEqual([{_barcode_scanned: "0123456789012"}]);
});

test("showQuantOperations only shows the operations of the given quant", () => {
    const container = document.createElement("div");
    for (const quantId of [1, 2]) {
        const operations = document.createElement("div");
        operations.className = `oe_kanban_operations oe_kanban_operations-${quantId} d-none`;
        container.appendChild(operations);
    }
    const [first, second] = container.querySelectorAll(".oe_kanban_operations");

    showQuantOperations(container, 2);
    expect(first.classList.contains("d-none")).toBe(true);
    expect(second.classList.contains("d-none")).toBe(false);

    showQuantOperations(container, 1);
    expect(first.classList.contains("d-none")).toBe(false);
    expect(second.classList.contains("d-none")).toBe(true);
});
