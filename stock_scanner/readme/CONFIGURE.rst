In Odoo
~~~~~~~

Declare hardware
~~~~~~~~~~~~~~~~

You have to declare some hardware scanners in Odoo.

Go to "Inventory > Configuration > Scanner Configuration > Scanner Hardware" and create a new record.

The "step type code" sent by the "odoo-sentinel" client at start-up is the IP address of the hardware, if connected through SSH.

If needed enable Login/Logout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The module comes with 2 predefined scenarii for Login and Logout. The functionality is disabled by default and the user to use in
Odoo must be specified in the `.odoorpcrc` file used by odoo-sentinel and can be overriden on the Scanner Hardware definition
in Odoo.

If the Login/logout functionality is enabled, when a user starts a session with odoo-sentinel, only the Login scenario is displayed on the
screen. The scenario will prompt the user for its login and pwd. If the authentication succeeds, each interaction with Odoo will be done
using the uid of the connected user. Once connected, a Logout scenario is displayed in the list of available scenarii and the Login
scenario no longer appears.

The Login/logout functionality enables you to specify on the scenario a list of users and/or a list of groups with access to the scenario.

To enable the Login/logout functionality:
    * Go to "Settings > Warehouse" and check the checkbox Login/logout scenarii enabled.
    * Create a *Technical User* 'sentinel' **without roles in Human Resources** and with 'Sentinel: technical users' checked.
    * Use this user to launch your odoo-sentinel session.

Be careful, the role *Sentinel: technical users* is a technical role and should only be used by sentinel.

The timeout of sessions is managed by a dedicated cron that resets the inactive sessions. The timeout can be configured on
settings. "Settings > Warehouse"

For the odoo-sentinel client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The odoo-sentinel client uses an OdooRPC profile to connect to Odoo.
The default configuration file is `~/.odoorpcrc`, but this can be customized, using the `-c`/`--config` argument.
See the `hardware/odoorpcrc.sample` file for an example.

If the `-p`/`--profile` argument is not given on the command line, a profile named `sentinel` will be used.

The file used to log errors can be defined by using the `-l`/`--log-file` argument, which defaults to `~/sentinel.log`.

**Note** : If you want to copy the application outside this git repository, you will need to copy the i18n folder too.

Autoconfiguration feature
~~~~~~~~~~~~~~~~~~~~~~~~~

The `odoo-sentinel` client has an autoconfiguration feature, used to automatically recognize the hardware being connected.
During initialization, the `odoo-sentinel` client tries to detect an SSH connection, and sends the terminal's IP address as terminal code.
If the IP address is found on the `code` field on a configured hardware in the database, this hardware configuration will automatically be used.
If the IP address is not found, the client will ask the user to type (or scan) a code.

This can be used only if the Odoo server and the connected hardware are on the same network.

Writing scenario
~~~~~~~~~~~~~~~~~

Creation
~~~~~~~~

The preferred way to start the creation of a scenario is to create steps and transitions in diagram view.

Once your steps are created, you can write python code directly from Odoo, or you can export the scenario to write the python code with your preferred code editor.

In the python code of each step, some variables are available :
    - cr : Cursor to the database
    - uid : ID of the user executing the step (user used to log in with the sentinel, or user configured on the hardware, if any)
    - pool : Pooler to the database
    - env : Environment used to execute the scenario (new API)
    - model : Pooler on the model configured on the scenario
    - term : Recordset on the current scenario
    - context : Context used on the step
    - m or message : Last message sent by the hardware
    - t or terminal : Browse record on the hardware executing the step
    - tracer : Value of the tracer of the used transition to access this step
    - wkf or workflow : Workflow service
    - scenario : Recordset on the current scenario for the hardware
    - _ : The translation function provided by Odoo (useable like in any other python file)

Some of these variables are also available on transition conditions execution.

As stated previously, the step must always return:

- A step type code, in the `act` variable
- A message to display on the hardware screen, in the `res` variable
- Optionally, a default value, in the `val` variable

Step types
~~~~~~~~~~

The step types are mostly managed by the client.

The standard step types are :

- M : Simple message
- F : Final step, like M, but ends the scenario
- T : Text input
- N : Number input (integer)
- Q : Quantity input (float)
- L : List
- E : Error message, like M, but displayed with different colors
- C : Confirm input
- A : Automatic step. This type is used to automatically execute the next step

.. note::

   The automatic step often needs to define a value in `val`, corresponding to the value the user must send.
   This step type is generally used as replacement of another type, at the end of the step code, by redefining the `act` variable in some cases, for example when a single value is available for a list step.

Import
~~~~~~

Scenarios are automatically imported on a module update, like any other data.
You just have to add the path to your `Scenario_Name.scenario` files in the `data` or `demo` sections in the `__manifest__.py` file.

Export
~~~~~~

The export script is in the `script` directory of the module

A scenario is exported as a set of files, containing :
    - Scenario_Name.scenario : Global description of the scenario (name, warehouses, steps, transitions, etc.)
    - A .py file per step : The name of the file is the XML ID of the step

Using a test file
~~~~~~~~~~~~~~~~~

When developing scenarios, you will often have the same steps to run.
The odoo-sentinel client allows you to supply a file, which contains the keys pressed during the scenario.

You can define the file to use in the `-t`/`--test-file` argument.
This file will be read instead of calling the curses methods when the scenario is waiting for a user input (including line feed characters).
When the file has been fully read, the client exits.

A sample test file can be found in the "Step Types" demo scenario.

*Special keys* :
For special keys (arrows, delete, etc.), you must write a line containing ':', followed by the curses key code.

Valid key codes are :
    - KEY_DOWN : Down arrow
    - KEY_UP : Up arrow
    - KEY_LEFT : Left arrow
    - KEY_RIGHT : Right arrow
    - KEY_BACKSPACE : Backspace
    - KEY_DC : Delete
