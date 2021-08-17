If you want to generate barcode for another model, you can create a custom
module that inherits on 'barcodes_generator_abstract' and inherit your model
like that:

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['my.model', 'barcode.generate.mixin']

class barcode_rule(models.Model):
    _inherit = 'barcode.rule'

    generate_model = fields.Selection(selection_add=[('my.model', 'My Model')])

Finally, you should inherit your model view adding buttons and fields.

Note
~~~~

Your model should have a field 'barcode' defined.
