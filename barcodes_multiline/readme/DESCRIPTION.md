This module extends Odoo's keyboard-wedge barcode scanning to preserve
newlines and tabs contained *inside* a barcode. The barcode is still
emitted as one `barcode_scanned` event after the scanner becomes idle.

For example, a scanner sending `SKU: A123`, Enter, `SERIAL: 12345`
produces a single barcode whose content contains a newline.

A final Enter or Tab sent by the scanner as a suffix is not included in
the barcode, so ordinary one-line scanners and barcode commands keep
working.

This module applies to keyboard-wedge scanners using the Odoo web
barcode service. Camera-based decoding is independent of the keyboard
event handling.
