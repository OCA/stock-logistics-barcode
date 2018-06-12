#! /usr/bin/env python3
# © 2011 Christophe CHAUVET <christophe.chauvet@syleam.fr>
# © 2011 Jean-Sébastien SUZANNE <jean-sebastien.suzanne@syleam.fr>
# © 2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# © 2018 Chris Tribbeck <chris.tribbeck@subteno-it.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import logging
import re
import odoorpc
import os
import sys

from lxml.etree import Element, ElementTree, SubElement

parser = argparse.ArgumentParser(
    description='Scenarios export script for Odoo\'s stock_scanner module',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

connection_group = parser.add_argument_group('Connection')
connection_group.add_argument(
    '--host', dest='host', default='localhost',
    help='Address of the Odoo server.')
connection_group.add_argument(
    '-p', '--port', dest='port', default='8069',
    help='Port of the Odoo server.')
connection_group.add_argument(
    '-d', '--database', dest='database', default='demo',
    help='Database in which the scenario to export is created.')
connection_group.add_argument(
    '-u', '--user', dest='user', default='admin',
    help='User to export the scenario.')
connection_group.add_argument(
    '-w', '--password', dest='password', default='admin',
    help='Password of the user.')

export_group = parser.add_argument_group('Export')
export_group.add_argument(
    '-v', '--verbose', dest='verbose', default=False, action='store_true',
    help='Run in verbose mode.')
export_group.add_argument(
    '-i', '--id', dest='scenario_id', required=True, type=int,
    help='ID of the scenario to export.')
export_group.add_argument(
    '-n', '--name', dest='name',
    help='Name of the scenario to export.')
export_group.add_argument(
    '--directory', dest='directory', default='.',
    help='Directory where to write the exported scenario.')

options = parser.parse_args(sys.argv[1:])

logger = logging.getLogger("Export scenario")
log_channel = logging.StreamHandler()
if options.verbose:
    logger.setLevel(logging.DEBUG)
    log_channel.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    log_channel.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_channel.setFormatter(formatter)
logger.addHandler(log_channel)

try:
    logger.info(
        'Open connection to "%s:%s" on "%s" with user "%s" ',
        options.host, options.port, options.database, options.user)
    connection = odoorpc.ODOO(options.host, port=options.port)
    connection.login(
        options.database, login=options.user, password=options.password)
except Exception as e:
    logger.error('Fail to connect to the server')
    logger.error('%s' % str(e))
    sys.exit(1)


def normalize_name(name):
    """
    Replace all non alphanumeric characters by underscores
    """
    return re.sub(r'[^\w\d]', '_', name).lower()


def new_node(name, value):
    node = SubElement(root, name)
    node.text = value
    return node


step_xml_ids = {}
options.directory = os.path.expanduser(options.directory)

# Extract scenario
scenario_obj = connection.env['scanner.scenario']
scenario = scenario_obj.browse(options.scenario_id).with_context(
    # Force the en_US language to export translateable values
    active_test=False, lang='en_US')

scenario_xml_id = scenario.get_metadata()[0]['xmlid']
if not scenario_xml_id:
    scenario_xml_id = 'scanner_scenario_%s' % normalize_name(scenario.name)

# Add the scenario values in the XML structure
root = Element('scenario')
new_node('id', scenario_xml_id),
new_node('active', str(scenario.active)),
new_node('sequence', str(scenario.sequence)),
new_node('name', scenario.name),
new_node('type', scenario.type),
new_node('notes', scenario.notes or ''),

if scenario.model_id:
    new_node('model_id', scenario.model_id.model),

if scenario.company_id:
    new_node('company_id', scenario.company_id.name),

if scenario.parent_id:
    parent_value = scenario.parent_id.get_metadata()[0]['xmlid']
    if not parent_value:
        parent_value = 'scanner_scenario_{parent_name)'.format(
            parent_name=normalize_name(scenario.parent_id.name),
        )
    new_node('parent_id', parent_value)

for warehouse in scenario.warehouse_ids:
    warehouse_value = warehouse.get_metadata()[0]['xmlid']
    if not warehouse_value:
        warehouse_value = warehouse.name

    new_node('warehouse_ids', warehouse_value)

for user in scenario.user_ids:
    new_node('user_ids', user.login)

for group in scenario.group_ids:
    group_value = group.get_metadata()[0]['xmlid']
    if group_value:
        new_node('group_ids', group_value)

# Export steps
transitions = set()
sorted_steps = sorted(scenario.step_ids, key=lambda record: record.name)
step_xmlid_counters = {}
for step in sorted_steps:
    # Retrieve the step's xml ID
    step_xml_id = step.get_metadata()[0]['xmlid']
    if not step_xml_id:
        step_xml_id = 'scanner_scenario_step_{scenario}_{step}'.format(
            scenario=normalize_name(scenario.name),
            step=normalize_name(step.name),
        )

    if step_xml_id in step_xmlid_counters:
        step_xmlid_counters[step_xml_id] += 1
        step_xml_id += '_%d' % (step_xmlid_counters[step_xml_id])
        step_xmlid_counters[step_xml_id] = 1
        # This prevents problems with 2 steps named 'test' [generating 'test'
        # and 'test_2'] and a third step named 'test_2' [with this code, it
        # will generate 'test_2_2']
    else:
        step_xmlid_counters[step_xml_id] = 1

    step_xml_ids[step.id] = step_xml_id

    # Do not add the scenario name on the python filename
    # if this step is defined in the same module as the scenario
    python_filename = step_xml_id
    if '.' in scenario_xml_id and '.' in step_xml_id:
        scenario_module = scenario_xml_id.split('.')[0]
        step_module = step_xml_id.split('.')[0]
        if scenario_module == step_module:
            python_filename = step_xml_id.split('.')[1]

    # Save the code of the step in a python file
    with open('%s/%s.py' % (options.directory, python_filename), 'w') as\
            step_file:
        step_file.write(step.python_code)

    step_attributes = {'id': step_xml_id}
    for field in ['name', 'step_start', 'step_stop', 'step_back', 'no_back']:
        step_attributes[field] = str(step[field])

    SubElement(root, 'Step', attrib=step_attributes)

    # Store the transitions of this step
    transitions.update(step.out_transition_ids)

# Export transitions
transition_xmlid_counters = {}
sorted_transitions = sorted(transitions, key=lambda record: record.name)
for transition in sorted_transitions:
    # Retrieve the transition's xml ID
    transition_xml_id = transition.get_metadata()[0]['xmlid']
    if not transition_xml_id:
        transition_xml_id = 'scanner_scenario_{scenario}_{transition}'.format(
            scenario=normalize_name(scenario.name),
            transition=normalize_name(transition.name),
        )

    if transition_xml_id in transition_xmlid_counters:
        transition_xmlid_counters[transition_xml_id] += 1
        transition_xml_id += '_%d' %\
            (transition_xmlid_counters[transition_xml_id])
        transition_xmlid_counters[transition_xml_id] = 1
        # This prevents problems with 2 transitions named 'test' [generating
        # 'test' and 'test_2'] and a third transition named 'test_2' [with
        # this code, it will generate 'test_2_2']
    else:
        transition_xmlid_counters[transition_xml_id] = 1

    transition_attributes = {
        'id': transition_xml_id,
        'name': transition.name,
        'sequence': str(transition.sequence),
        'to_id': step_xml_ids[transition.to_id.id],
        'from_id': step_xml_ids[transition.from_id.id],
        'condition': transition.condition,
        'transition_type': transition.transition_type,
        # Don't write False in the "tracer" attribute
        'tracer': transition.tracer or '',
    }
    SubElement(root, 'Transition', attrib=transition_attributes)

scenario_name = options.name
if not scenario_name:
    scenario_name = os.path.split(options.directory.strip('/'))[1]

xml_filename = os.path.join(
    options.directory,
    '{scenario}.scenario'.format(scenario=scenario_name),
)
with open(xml_filename, 'wb') as xml_file:
    ElementTree(root).write(
        xml_file, encoding='UTF-8', xml_declaration=True, pretty_print=True)
