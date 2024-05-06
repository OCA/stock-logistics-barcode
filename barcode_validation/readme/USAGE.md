This module is an abstract module. You can configure barcode validation, but to enable this feature, you need to install an extra module for a given model. This repository provide 'product_barcode_validation' and 'stock_barcode_validation' to validate barcodes for products, stock lots, product packagings, ...

Alternatively, you can develop a custom module for a custom model. See
'Inheritance' parts.

If you want to validate barcode for another model, you can create a custom
module that depend on 'barcode_validation_abstract' and inherit your model
like that:

```python
  class MyModel(models.Mode)
    _name = "my.model"
    _inherit = ["my.model", "barcode.validation.mixin"]

    @api.constrains("field_barcode")
    def check_barcode_validation(self):
        for record in self.filtered("field_barcode"):
          record._validate_barcode(record.field_barcode)
```
