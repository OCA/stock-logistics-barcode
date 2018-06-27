# © 2011 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import random
import time
import datetime

from psycopg2 import OperationalError, errorcodes

from odoo import models, api, fields, exceptions
from odoo import _
from odoo.tools.misc import ustr, html_escape
from odoo.tools.safe_eval import safe_eval


logger = logging.getLogger('stock_scanner')

_CURSES_COLORS = [
    ('black', _('Black')),
    ('blue', _('Blue')),
    ('cyan', _('Cyan')),
    ('green', _('Green')),
    ('magenta', _('Magenta')),
    ('red', _('Red')),
    ('white', _('White')),
    ('yellow', _('Yellow')),
]

PG_CONCURRENCY_ERRORS_TO_RETRY = (
    errorcodes.LOCK_NOT_AVAILABLE,
    errorcodes.SERIALIZATION_FAILURE,
    errorcodes.DEADLOCK_DETECTED)
MAX_TRIES_ON_CONCURRENCY_FAILURE = 5


class ScannerHardware(models.Model):
    _name = 'scanner.hardware'
    _description = 'Scanner Hardware'

    @api.model
    def _colors_get(self):
        return _CURSES_COLORS

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the hardware.')
    code = fields.Char(
        string='Code',
        required=True,
        help='Code of this hardware.')
    log_enabled = fields.Boolean(
        string='Log enabled',
        default=False,
        help='Enable logging messages from scenarios.')
    screen_width = fields.Integer(
        string='Screen Width',
        default=20,
        required=False,
        help='Width of the terminal\'s screen.')
    screen_height = fields.Integer(
        string='Screen Height',
        default=4,
        required=False,
        help='Height of the terminal\'s screen.')
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        ondelete='restrict',
        help='Warehouse where is located this hardware.')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=False,
        ondelete='restrict',
        help='Allow to define an other user for execute all scenarios with '
             'that scanner instead of default user.')
    last_call_dt = fields.Datetime(
        string='Last call',
        help='Date and time of the last call to the system done by the '
        'scanner.'
    )
    scenario_id = fields.Many2one(
        comodel_name='scanner.scenario',
        string='Scenario',
        required=False,
        readonly=True,
        default=False,
        ondelete='restrict',
        help='Scenario used for this hardware.')
    step_id = fields.Many2one(
        comodel_name='scanner.scenario.step',
        string='Current Step',
        required=False,
        readonly=True,
        default=False,
        ondelete='restrict',
        help='Current step for this hardware.')
    step_history_ids = fields.One2many(
        comodel_name='scanner.hardware.step.history',
        inverse_name='hardware_id', string='Steps History',
        readonly=True,
        help='History of all steps executed by this hardware'
        ' during the current scenario.')
    reference_document = fields.Integer(
        string='Reference',
        default=0,
        required=False,
        readonly=True,
        help='ID of the reference document.')
    base_fg_color = fields.Selection(
        selection='_colors_get',
        string='Base - Text Color',
        required=True,
        default='white',
        help='Default color for the text.')
    base_bg_color = fields.Selection(
        selection='_colors_get',
        string='Base - Background Color',
        required=True,
        default='blue',
        help='Default color for the background.')
    info_fg_color = fields.Selection(
        selection='_colors_get',
        string='Info - Text Color',
        required=True,
        default='yellow',
        help='Color for the info text.')
    info_bg_color = fields.Selection(
        selection='_colors_get',
        string='Info - Background Color',
        required=True,
        default='blue',
        help='Color for the info background.')
    error_fg_color = fields.Selection(
        selection='_colors_get',
        string='Error - Text Color',
        required=True,
        default='yellow',
        help='Color for the error text.')
    error_bg_color = fields.Selection(
        selection='_colors_get',
        string='Error - Background Color',
        required=True,
        default='red',
        help='Color for the error background.')
    tmp_values = fields.Serialized(
        readonly=True
    )
    tmp_values_display = fields.Html(
        compute='_compute_tmp_values_display',
        help="Debug tmp values",
    )

    @api.depends('tmp_values')
    def _compute_tmp_values_display(self):
        for rec in self:
            txt = [
                '<table><tr>',
                '<th>' + html_escape(_('Key')) + '</th>',
                '<th>' + html_escape(_('Value')) + '</th></tr>',
            ]
            for key in sorted(rec.tmp_values.keys()):
                val = rec.tmp_values[key]
                txt.append(
                    '<tr><td>%s</td><td>%s</td></tr>' %
                    (html_escape(key), html_escape(val))
                )
            txt.append('</table>')
            rec.tmp_values_display = ''.join(txt)

    # The json_tmp_valN properties are kept as a compatibility layer to
    # help scenario migration. You should use the tmp_values field
    # instead. These will be removed when the module is migrated to
    # Odoo 12.0
    @property
    @api.multi
    def json_tmp_val1(self):
        self.ensure_one()
        return self.get_tmp_value('val1')

    @json_tmp_val1.setter
    def json_tmp_val1(self, value):
        self.ensure_one()
        self.update_tmp_values({'val1': value})

    @property
    @api.multi
    def json_tmp_val2(self):
        self.ensure_one()
        return self.get_tmp_value('val2')

    @json_tmp_val2.setter
    def json_tmp_val2(self, value):
        self.ensure_one()
        self.update_tmp_values({'val2': value})

    @property
    @api.multi
    def json_tmp_val3(self):
        self.ensure_one()
        return self.get_tmp_value('val3')

    @json_tmp_val3.setter
    def json_tmp_val3(self, value):
        self.ensure_one()
        self.update_tmp_values({'val3': value})

    @property
    @api.multi
    def json_tmp_val4(self):
        self.ensure_one()
        return self.get_tmp_value('val4')

    @json_tmp_val4.setter
    def json_tmp_val4(self, value):
        self.ensure_one()
        self.update_tmp_values({'val4'})

    @property
    @api.multi
    def json_tmp_val5(self):
        self.ensure_one()
        return self.get_tmp_value('val5')

    @json_tmp_val5.setter
    def json_tmp_val5(self, value):
        self.ensure_one()
        self.update_tmp_values({'val5': value})

    @api.multi
    def update_tmp_values(self, values):
        self.ensure_one()
        tmp_values = self.tmp_values
        tmp_values.update(values)
        self.write({'tmp_values': tmp_values})

    @api.multi
    def get_tmp_value(self, key_name, default=None):
        self.ensure_one()
        return self.tmp_values.get(key_name, default)

    @api.multi
    def set_tmp_value(self, key_name, value):
        self.ensure_one()
        self.update_tmp_values({
            key_name: value,
        })

    @api.multi
    def clean_tmp_values(self, items):
        self.ensure_one()
        values = self.tmp_values
        for item in items:
            values.pop(item, None)
        self.update_tmp_values(values)

    @api.model
    def timeout_session(self):
        timeout_delay = self.env['ir.config_parameter'].get_param(
            'hardware_scanner_session_timeout', 1800)  # seconds
        expired_dt = datetime.datetime.now() - datetime.timedelta(
            seconds=int(timeout_delay))
        expired_str = fields.Datetime.to_string(expired_dt)
        terminals = self.search([('last_call_dt', '<', expired_str)])
        terminals.logout()
        terminals.empty_scanner_values()

    @api.model
    def _get_terminal(self, terminal_number):
        terminal = self.search([('code', '=', terminal_number)])
        terminal.ensure_one()
        return terminal

    @api.model
    def scanner_check(self, terminal_number):
        terminal = self._get_terminal(terminal_number)
        uid = terminal.user_id.id or self.env.uid
        terminal = terminal.sudo(uid)
        return terminal.scenario_id and (
            terminal.scenario_id.id,
            terminal.scenario_id.name) or False

    @api.model
    def scanner_call(self, terminal_number, action, message=False,
                     transition_type='keyboard'):
        """
        This method is called by the barcode reader,
        """
        # Retrieve the terminal id
        terminal = self._get_terminal(terminal_number)
        if terminal.user_id.id:
            # only reset last call if user_id
            terminal.last_call_dt = fields.Datetime.now()
        # Change uid if defined on the stock scanner
        uid = terminal.user_id.id or self.env.uid
        return terminal.sudo(uid)._scanner_call(
            action, message=message, transition_type=transition_type)

    def _scanner_call(self, action, message=False,
                      transition_type='keyboard'):
        self.ensure_one()
        scanner_scenario_obj = self.env['scanner.scenario']
        # Retrieve the terminal screen size
        if action == 'screen_size':
            logger.debug('Retrieve screen size')
            screen_size = self._screen_size()
            return ('M', screen_size, 0)

        # Retrieve the terminal screen colors
        if action == 'screen_colors':
            logger.debug('Retrieve screen colors')
            screen_colors = {
                'base': (self.base_fg_color, self.base_bg_color),
                'info': (self.info_fg_color, self.info_bg_color),
                'error': (self.error_fg_color, self.error_bg_color),
            }
            return ('M', screen_colors, 0)

        # Execute the action
        elif action == 'action':
            # The terminal is attached to a scenario
            if self.scenario_id:
                return self._scenario_save(
                    message,
                    transition_type,
                    scenario_id=self.scenario_id.id,
                    step_id=self.step_id.id,
                )
            # We asked for a scan transition type, but no action is running,
            # forbidden
            elif transition_type == 'scanner':
                return self._unknown_action(message)
            # No action to do
            else:
                logger.info('[%s] Action : %s (no current scenario)',
                            self.code, message)
                scenario_ids = scanner_scenario_obj.search([
                    ('name', '=', message),
                    ('type', '=', 'menu'),
                    '|',
                    ('warehouse_ids', '=', False),
                    ('warehouse_ids', 'in', [self.warehouse_id.id]),
                ])
                if scenario_ids:
                    scenarios = self._scenario_list(
                        parent_id=scenario_ids.id)
                    if scenarios:
                        menu_name = scenario_ids[0].name
                        return ('L', ['|%s' % menu_name] + scenarios, 0)
                return self._scenario_save(message, transition_type)

        # Reload current step
        elif action == 'restart':
            # The terminal is attached to a scenario
            if self.scenario_id:
                return self._scenario_save(
                    message,
                    'restart',
                    scenario_id=self.scenario_id.id,
                    step_id=self.step_id.id,
                )

        # Reload previous step
        elif action == 'back':
            # The terminal is attached to a scenario
            if self.scenario_id:
                return self._scenario_save(
                    message,
                    'back',
                    scenario_id=self.scenario_id.id,
                    step_id=self.step_id.id,
                )

        # End required
        elif action == 'end':
            # Empty the values
            logger.info('[%s] End scenario request' % self.code)
            self.sudo().empty_scanner_values()

            return ('F', [_('This scenario'), _('is finished')], '')

        # If the terminal is not attached to a scenario, send the menu
        # (scenario list)
        if not self.scenario_id:
            logger.info('[%s] No running scenario' % self.code)
            scenarios = self._scenario_list(message)
            return ('L', scenarios, 0)

        # Nothing matched, return an error
        return self._send_error(['Unknown action'])

    def _send_error(self, message):
        """
        Sends an error message
        """
        self.ensure_one()
        self.sudo().empty_scanner_values()
        return ('R', message, 0)

    @api.model
    def _unknown_action(self, message):
        """
        Sends an unknown action message
        """
        return ('U', message, 0)

    def empty_scanner_values(self):
        """
        This method empty all temporary values, scenario, step and
        reference_document
        Because if we want reset term when error we must use sql query,
        it is bad in production
        """
        self.write({
            'scenario_id': False,
            'step_id': False,
            'step_history_ids': [
                (2, history.id) for history in self.step_history_ids
            ],
            'reference_document': 0,
            'tmp_values': {},
        })
        return True

    @api.model
    def scanner_end(self, numterm=None):
        """
        End the end barcode is read, we execute this step
        """
        return self.scanner_call(terminal_number=numterm, action='end')

    @api.model
    def check_credentials(self, login, password):
        res_users = self.env['res.users']
        try:
            user = res_users.search([('login', '=', login)])
            if user:
                res_users.sudo(user).check_credentials(password)
            return user.id
        except exceptions.AccessDenied:
            return False

    def login(self, login, password):
        """This method assign the uid associated to login
        as current user of the hardware.
        The method MUST be called on the last step since the login
        scenario will no more be visible by the current user once it will
        be assigned this one
        """
        self.ensure_one()
        uid = self.check_credentials(login, password)
        if uid:
            self.write({
                'user_id': uid,
                'last_call_dt': fields.Datetime.now(),
            })

    def logout(self):
        self.write({
            'user_id': False,
            'last_call_dt': False,
        })
        return True

    def _memorize(self, scenario_id, step_id, obj=None):
        """
        After affect a scenario to a scanner, we must memorize it
        If obj is specify, save it as well (ex: res.partner,12)
        """
        self.ensure_one()
        self.write({
            'scenario_id': scenario_id,
            'step_id': step_id,
        })

    def _do_scenario_save(self, message, transition_type, scenario_id=None,
                          step_id=None):
        """
        Save the scenario on this terminal and execute the current step
        Return the action to the terminal
        """
        self.ensure_one()
        scanner_scenario_obj = self.env['scanner.scenario']
        scanner_step_obj = self.env['scanner.scenario.step']
        terminal = self

        tracer = ''

        if (transition_type == 'restart' or
            transition_type == 'back' and
                terminal.scenario_id.id):
            if terminal.step_id.no_back:
                step_id = terminal.step_id.id
            else:
                last_call = terminal.step_history_ids[-1]

                # Retrieve last values
                step_id = last_call.step_id.id
                transition = last_call.transition_id
                tracer = last_call.transition_id.tracer
                message = safe_eval(last_call.message)

                # Prevent looping on the same step
                if transition.to_id == terminal.step_id and \
                   transition_type == 'back':
                    # Remove the history line
                    last_call.unlink()
                    return self._do_scenario_save(
                        message, transition_type,
                        scenario_id=scenario_id, step_id=step_id,
                    )

        # No scenario in arguments, start a new one
        if not self.scenario_id.id:
            # Retrieve the terminal's warehouse
            terminal_warehouse_ids = terminal.warehouse_id.ids
            # Retrieve the warehouse's scenarios
            scenario_ids = scanner_scenario_obj.search([
                ('name', '=', message),
                ('type', '=', 'scenario'),
                '|',
                ('warehouse_ids', '=', False),
                ('warehouse_ids', 'in', terminal_warehouse_ids),
            ])

            # If at least one scenario was found, pick the start step of the
            # first
            if scenario_ids:
                scenario_id = scenario_ids[0].id
                step_ids = scanner_step_obj.search([
                    ('scenario_id', '=', scenario_id),
                    ('step_start', '=', True),
                ])

                # No start step found on the scenario, return an error
                if not step_ids:
                    return self._send_error([
                        _('No start step found on the scenario'),
                    ])

                step_id = step_ids[0].id
                # Store the first step in terminal history
                terminal.step_history_ids.create({
                    'hardware_id': terminal.id,
                    'step_id': step_id,
                    'message': repr(message)
                })

            else:
                return self._send_error([_('Scenario not found')])

        elif transition_type not in ('back', 'none', 'restart'):
            # Retrieve outgoing transitions from the current step
            transition_obj = self.env['scanner.scenario.transition']
            transitions = transition_obj.search([('from_id', '=', step_id)])

            # Evaluate the condition for each transition
            for transition in transitions:
                step_id = False
                ctx = {
                    'context': self.env.context,
                    'model': self.env[
                        transition.from_id.scenario_id.model_id.sudo().model],
                    'cr': self.env.cr,
                    'pool': self.pool,
                    'env': self.env,
                    'uid': self.env.uid,
                    'm': message,
                    'message': message,
                    't': self,
                    'terminal': self,
                }
                try:
                    expr = safe_eval(str(transition.condition), ctx)
                except:
                    logger.exception(
                        "Error when evaluating transition condition\n%s",
                        transition.condition)
                    raise

                # Invalid condition, evaluate next transition
                if not expr:
                    continue

                # Condition passed, go to this step
                step_id = transition.to_id.id
                tracer = transition.tracer

                # Store the old step id if we are on a back step
                if transition.to_id.step_back and (
                    not terminal.step_history_ids or
                    terminal.step_history_ids[-1].transition_id != transition
                ):
                    terminal.step_history_ids.create({
                        'hardware_id': terminal.id,
                        'step_id': transition.to_id.id,
                        'transition_id': transition.id,
                        'message': repr(message)
                    })

                # Valid transition found, stop searching
                break

            # No step found, return an error
            if not step_id:
                terminal.log('No valid transition found !')
                return self._unknown_action([
                    _('Please contact'),
                    _('your'),
                    _('administrator'),
                ])

        # Memorize the current step
        terminal._memorize(scenario_id, step_id)

        # Execute the step
        step = terminal.step_id

        ld = {
            'cr': self.env.cr,
            'uid': self.env.uid,
            'pool': self.pool,
            'env': self.env,
            'model': self.env[step.scenario_id.model_id.sudo().model],
            'term': self,
            'context': self.env.context,
            'm': message,
            'message': message,
            't': terminal,
            'terminal': terminal,
            'tracer': tracer,
            'scenario': terminal.scenario_id,
            '_': _,
        }

        terminal.log('Executing step %d : %s' % (step_id, step.name))
        terminal.log('Message : %s' % repr(message))
        if tracer:
            terminal.log('Tracer : %s' % repr(tracer))

        exec(step.python_code, ld)
        if step.step_stop:
            terminal.empty_scanner_values()

        return (
            ld.get('act', 'M'),
            ld.get('res', ['nothing']),
            ld.get('val', 0),
        )

    def _scenario_save(self, message, transition_type, scenario_id=None,
                       step_id=None):
        """
        Save the scenario on this terminal, handling transient errors by
        retrying the same step
        Return the action to the terminal
        """
        self.ensure_one()
        result = ('M', ['TEST'], False)
        tries = 0
        while True:
            try:
                result = self._do_scenario_save(
                    message,
                    transition_type,
                    scenario_id=scenario_id,
                    step_id=step_id,
                )
                break
            except OperationalError as e:
                # Automatically retry the typical transaction serialization
                # errors
                self.env.cr.rollback()
                if e.pgcode not in PG_CONCURRENCY_ERRORS_TO_RETRY:
                    logger.warning(
                        "[%s] OperationalError",
                        self.code,
                        exc_info=True)
                    result = ('R', [
                        'Please contact', 'your', 'administrator',
                    ], 0)
                    break
                if tries >= MAX_TRIES_ON_CONCURRENCY_FAILURE:
                    logger.warning(
                        "[%s] Concurrent transaction - "
                        "OperationalError %s, maximum number of tries reached",
                        self.code,
                        e.pgcode)
                    result = ('E', [
                        ustr('Concurrent transaction - OperationalError '
                             '%s, maximum number of tries reached') %
                        (e.pgcode),
                    ], True)
                    break
                wait_time = random.uniform(0.0, 2 ** tries)
                tries += 1
                logger.info(
                    "[%s] Concurrent transaction detected (%s), "
                    "retrying %d/%d in %.04f sec...",
                    self.code,
                    e.pgcode,
                    tries,
                    MAX_TRIES_ON_CONCURRENCY_FAILURE,
                    wait_time)
                time.sleep(wait_time)
            except (exceptions.except_orm, exceptions.UserError) as e:
                # ORM exception, display the error message and require the "go
                # back" action
                self.env.cr.rollback()
                logger.warning('[%s] OSV Exception:', self.code, exc_info=True)
                result = ('E', [e.name or '', '', e.value or ''], True)
                break
            except Exception as e:
                self.env.cr.rollback()
                logger.error('[%s] Exception: ', self.code, exc_info=True)
                result = ('R', ['Please contact', 'your', 'administrator'], 0)
                self.empty_scanner_values()
                break
        self.log('Return value : %r' % (result,))

        # Manage automatic steps
        if result[0] == 'A':
            return self.scanner_call(self.code, 'action', message=result[2])

        return result

    @api.model
    def _scenario_list(self, parent_id=False):
        """
        Retrieve the scenario list for this warehouse
        """
        scanner_scenario_obj = self.env['scanner.scenario']
        scanner_scenario_ids = scanner_scenario_obj.search([
            '|',
            ('warehouse_ids', '=', False),
            ('warehouse_ids', 'in', [self.warehouse_id.id]),

            ('parent_id', '=', parent_id),
            '|',
            ('child_ids', '!=', False),
            ('step_ids', '!=', False)
        ])

        return scanner_scenario_ids.mapped('name')

    @api.multi
    def _screen_size(self):
        """
        Retrieve the screen size for this terminal
        """
        self.ensure_one()
        return (self.screen_width, self.screen_height)

    def log(self, log_message):
        if self.log_enabled:
            logger.info('[%s] %s' % (self.code, ustr(log_message)))
