To use this module, you need to:

- Define, in the view, the button that will be clicked automatically as
  the example below. Use the `d-none` class (instead of `invisible="1"`)
  to hide the button, so it is kept in the DOM:

``` xml
<button name="action_automatic_entry" type="object" string="Automatic entry" icon="fa-plus"
        class="btn-primary barcode-automatic-entry d-none"
/>
```

- Define the logic to be executed upon button clicking

``` python
def action_automatic_entry(self):
    # Execute specific logic
    return
```
