# Copyright 2017 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestStockScannerHardware(common.TransactionCase):
    def setUp(self):
        ret = super(TestStockScannerHardware, self).setUp()

        self.hardware = self.env.ref('stock_scanner.scanner_hardware_1')

        return ret

    def test_check_scenario_without_running_scenario(self):
        """ Should return False when no scenario is running on the hardware """
        self.assertFalse(
            self.env['scanner.hardware'].scanner_check(self.hardware.code))

    def test_check_scenario_with_running_scenario(self):
        """ Should return the scenario id and name from an existing hardware
        """
        scenario = self.env.ref('stock_scanner.scanner_scenario_tutorial')
        self.hardware.scenario_id = scenario

        values = self.env['scanner.hardware'].scanner_check(self.hardware.code)
        scenario_id, scenario_name = values

        self.assertEqual(scenario_id, scenario.id)
        self.assertEqual(scenario_name, scenario_name)

    def test_wrong_credentials(self):
        """ Should not write the date when trying to login sith a wrong password
        """
        uid = self.hardware.check_credentials('wrong login', 'wrong password')
        self.assertEqual(False, uid)

    def test_wrong_login(self):
        """ Should not write the date when trying to login sith a wrong password
        """
        last_date = self.hardware.last_call_dt
        self.hardware.login('demo', 'wrong password')
        self.assertEqual(last_date, self.hardware.last_call_dt)

    def test_no_back(self):
        """ Should not return back to the previous step if no_back """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Check linked scenario and step
        self.assertEqual(self.hardware.scenario_id, scenario_step_types)
        scenario_step_introduction = self.env.ref(
            'stock_scanner.scanner_scenario_step_step_types_introduction')
        self.assertEqual(self.hardware.step_id, scenario_step_introduction)

        # Go to the next step
        scanner_hardware.scanner_call(self.hardware.code, action='action')

        # Check new linked step
        scenario_step_message = self.env.ref(
            'stock_scanner.scanner_scenario_step_step_types_message')
        self.assertEqual(self.hardware.step_id, scenario_step_message)

        # Define the current step as no_back
        scenario_step_message.no_back = True

        # Call the back action
        scanner_hardware.scanner_call(self.hardware.code, action='back')

        # The linked step shouldn't have been changed
        self.assertEqual(self.hardware.step_id, scenario_step_message)

    def test_step_back_on_the_first_step(self):
        """ Should restart the first step on back action """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Check linked scenario and step
        self.assertEqual(self.hardware.scenario_id, scenario_step_types)
        scenario_step_introduction = self.env.ref(
            'stock_scanner.scanner_scenario_step_step_types_introduction')
        self.assertEqual(self.hardware.step_id, scenario_step_introduction)

        # Call the back action
        scanner_hardware.scanner_call(self.hardware.code, action='back')

        # The scenario should have been restarted
        self.assertEqual(self.hardware.scenario_id, scenario_step_types)

    def test_scenario_with_no_start_step(self):
        """ Should return an error when there is no start step """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Remove the start step of the scenario
        scenario_step_introduction = self.env.ref(
            'stock_scanner.scanner_scenario_step_step_types_introduction')
        scenario_step_introduction .step_start = False

        # Launch the Step types scenario
        ret = scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # The scenario should have been restarted
        self.assertEqual(ret, ('R', [
            'No start step found on the scenario',
        ], 0))

    def test_no_transition(self):
        """ Should not do anything when there is no transition """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        ret = scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Remove all outgoing transitions from the current step
        self.hardware.step_id.out_transition_ids.unlink()

        # Try to go to the next step
        new_ret = scanner_hardware.scanner_call(
            self.hardware.code, action='action')
        self.assertEqual(new_ret, ret)

    def test_no_valid_transition(self):
        """ Should return an error when there is no valid transition """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Remove all outgoing transitions from the current step
        self.hardware.step_id.out_transition_ids.write({
            'condition': 'False',
        })

        # Try to go to the next step
        ret = scanner_hardware.scanner_call(
            self.hardware.code, action='action')
        self.assertEqual(ret, ('U', [
            'Please contact', 'your', 'administrator',
        ], 0))

    def test_transition_execution_error(self):
        """ Should return an error when a transition's condition crashes """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Remove all outgoing transitions from the current step
        self.hardware.step_id.out_transition_ids.write({
            'condition': 'undefined_function()',
        })

        # Try to go to the next step
        with mute_logger('stock_scanner'):
            ret = scanner_hardware.scanner_call(
                self.hardware.code, action='action')
        self.assertEqual(ret, ('R', [
            'Please contact', 'your', 'administrator',
        ], 0))

    def test_automatic_step(self):
        """ Should automatically go to the next step when automatic """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Remove all outgoing transitions from the current step
        scenario_step_message = self.env.ref(
            'stock_scanner.scanner_scenario_step_step_types_message')
        scenario_step_message.python_code = 'act = "A"'

        # Go to the next step
        ret = scanner_hardware.scanner_call(
            self.hardware.code, action='action')
        # We should be on the next next step
        self.assertEqual(ret, ('L', [
            ('|', 'List step'),
            ('error', 'Go to Error step'),
            ('continue', 'Go to next step'),
        ], 0))

    def test_log_from_scenario(self):
        """ Should write a line in the log when calling terminal.log

        This test doesn't actually really check that a line has been written,
        but simply ensures that using the method will not crash the scenario
        """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Activate the log for the current hardware
        self.hardware.log_enabled = True
        # Change the code of the next step to execute to write in the log
        scenario_step_message = self.env.ref(
            'stock_scanner.scanner_scenario_step_step_types_message')
        scenario_step_message.python_code = \
            "terminal.log('Testing the log method of scanner.hardware')\n" \
            "act = 'M'\n" \
            "res = []"

        # Go to the next step
        ret = scanner_hardware.scanner_call(
            self.hardware.code, action='action')
        # We should be on the next next step
        self.assertEqual(ret, ('M', [], 0))

    def test_log_tracer(self):
        """ Should write a line in the log when the transition has a tracer

        This test doesn't actually really check that a line has been written,
        but simply ensures that using a tracer will not crash the scenario
        """
        # Call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scenario_step_types = self.env.ref(
            'stock_scanner.scanner_scenario_step_types')

        # Launch the Step types scenario
        scanner_hardware.scanner_call(
            self.hardware.code, action='action',
            message=scenario_step_types.name)

        # Activate the log for the current hardware
        self.hardware.log_enabled = True
        # Change the code of the next step to execute to write in the log
        self.hardware.step_id.out_transition_ids.write({
            'tracer': 'something',
        })

        # Go to the next step
        ret = scanner_hardware.scanner_call(
            self.hardware.code, action='action')
        # We should be on the next next step
        self.assertEqual(ret, ('M', [
            '|Message step',
            '',
            'A step designed to display some information, '
            'without waiting for any user input.',
        ], 0))

    def test_legacy_shortcuts(self):
        self.assertEqual(self.hardware.json_tmp_val1, None)
        self.hardware.json_tmp_val2 = {'a': 'b', 'c': [1, 2, 3.5]}
        self.assertEqual(
            self.hardware.json_tmp_val2,
            {'a': 'b', 'c': [1, 2, 3.5]}
        )
        self.assertEqual(
            self.hardware.tmp_values,
            {'val2': {'a': 'b', 'c': [1, 2, 3.5]}}
        )

    def test_read_unitialized_json_value(self):
        """ Reading an uninitialized json value should return None """
        self.assertEqual(self.hardware.json_tmp_val1, None)

    def test_tmp_values_simple_value(self):
        hardware = self.hardware
        hardware.set_tmp_value('tmp_val_1', '')
        self.assertEqual(hardware.get_tmp_value('tmp_val_1'), '')

        hardware.set_tmp_value('tmp_float', 13.5)
        self.assertEqual(hardware.get_tmp_value('tmp_float'), 13.5)

        tmp_val_1 = 'test 1'
        tmp_val_2 = list(range(5))
        hardware.update_tmp_values({
            'tmp_val_1': 'test 1',
            'tmp_val_2': tmp_val_2,
        })
        self.assertEqual(hardware.get_tmp_value('tmp_val_1'), tmp_val_1)
        self.assertEqual(hardware.get_tmp_value('tmp_val_2'), tmp_val_2)

    def test_tmp_values_dict_value(self):
        hardware = self.hardware

        tmp_val_1 = 'test 1'
        tmp_val_2 = list(range(5))

        hardware.set_tmp_value('tmp_dict', {
            'extra_1': tmp_val_1,
            'extra_2': tmp_val_2,
        })
        self.assertEqual(hardware.get_tmp_value('tmp_dict'), {
            'extra_1': tmp_val_1,
            'extra_2': tmp_val_2,
        })
        self.assertEqual(
            hardware.get_tmp_value('tmp_dict').get('extra_1'),
            tmp_val_1)

    def test_tmp_values_clean_values(self):
        hardware = self.hardware
        hardware.tmp_values = {'a': 1, 'b': 2}
        self.assertNotEqual(hardware.tmp_values, {})

        hardware.clean_tmp_values(['a'])
        self.assertEqual(hardware.tmp_values, {'b': 2})

        self.assertTrue(bool(hardware.tmp_values))
        hardware.empty_scanner_values()
        self.assertFalse(bool(hardware.tmp_values))

    def test_unexisting_tmp_values(self):
        hardware = self.hardware
        hardware.empty_scanner_values()
        self.assertFalse(hardware.get_tmp_value('none'), None)
        self.assertFalse(
            hardware.get_tmp_value('false', default=False), False)
