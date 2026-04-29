You can integrate the scanner into your module by defining a client action:

```xml
<record id="action_scan_example" model="ir.actions.client">
    <field name="name">Scan Code</field>
    <field name="tag">web_ir_actions_client_scan.scan</field>
    <field name="res_model">example_model</field>
    <field name="params" eval="&quot;{ 'method': 'example_method' }&quot;"/>
</record>
```
The parameter is as follows:

- **method**: Used to determine which method of the res_model will be executed
 during scanning pocess.

Then trigger it from a button:
```xml
<button name="%(action_scan_example)d"
        type="action"
        string="Scan Code"
        class="btn-primary"/>
```
The action opens a popup where you will have the option to scan a barcode.
After completing the scan, the method defined in the action parameters
will be executed.

The signature of the method should be like in next code:
```python
@api.model
def example_method(self, barcode):
    pass
```
