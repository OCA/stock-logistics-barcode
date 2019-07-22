Group separator
===============

When an "Application Identifiers" has variable-length data,
the barcodes must contain a special character (<GS>, group separator)
but as this is not an ASCII character. Some barcode readers will not include
this character: decoding the structured data will then be impossible. Other
readers will translate GS1 to ASCII character 29, but this character is not
printable, and some applications may not record it. Yet other readers will
let you configure how to map <GS>, which may help improve compatibility.
