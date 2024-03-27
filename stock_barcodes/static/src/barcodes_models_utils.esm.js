/** @odoo-module */
/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

const barcodeModels = [
    "stock.barcodes.action",
    "stock.picking",
    "stock.picking.type",
    "wiz.candidate.picking",
    "wiz.stock.barcodes.new.lot",
    "wiz.stock.barcodes.read",
    "wiz.stock.barcodes.read.inventory",
    "wiz.stock.barcodes.read.picking",
    "wiz.stock.barcodes.read.todo",
];

export function isAllowedBarcodeModel(modelName) {
    return barcodeModels.indexOf(modelName) !== -1;
}
