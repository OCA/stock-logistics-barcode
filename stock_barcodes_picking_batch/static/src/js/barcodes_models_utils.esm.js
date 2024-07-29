/** @odoo-module */
/* Copyright 2024 Tecnativa - Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {barcodeModels} from "@stock_barcodes/utils/barcodes_models_utils.esm";

barcodeModels.push("stock.picking.batch", "wiz.candidate.picking.batch");
