#!/usr/bin/env python3
#
# This is used by the continuous integration script to validate the
# bytecodes.yaml file.
#

import re
import sys
import yaml

failed = False

def perr(message):
    global failed
    failed = True

    print(message, file=sys.stderr)

def check_code_info(name, info, allow_SUBP):
    # 'value' is required and must be an integer
    if 'value' in info:
        if not type(info['value']) is int:
            perr("%s 'value' is not an integer" % name)
        info.pop('value')
    else:
        perr("%s is missing 'value'" % name)

    # 'desc' is optional and must be a string
    if 'desc' in info:
        if not type(info['desc']) is str:
            perr("%s 'desc' is not a string" % name)
        info.pop('desc')

    # 'remarks' is optional and must be a string
    if 'remarks' in info:
        if not type(info['remarks']) is str:
            perr("%s 'remarks' is not a string" % name)
        info.pop('remarks')

    # 'params' is required and must be a list
    if 'params' in info:
        params = info['params']
        if type(params) is list:
            for i, param in enumerate(params):
                # 'name' is optional (for now) and must be a string
                if 'name' in param:
                    if not type(param['name']) is str:
                        perr("%s param %d 'name' is not a string" % (name, i))
                    param.pop('name')

                # 'desc' is optional and must be a string
                if 'desc' in param:
                    if not type(param['desc']) is str:
                        perr("%s param %d 'desc' is not a string" % (name, i))
                    param.pop('desc')

                # 'type' is required and must be a a valid type
                if 'type' in param:
                    if not param['type'] in ('PAR8', 'PAR16', 'PAR32', 'PARF',
                       'PARV', 'PARS', 'PARNO', 'PARVALUES', 'PARLAB', 'SUBP'):
                        perr("%s param %d 'type' is not a valid type ('%s')" %
                            (name, i, param['type']))
                    elif param['type'] == 'SUBP':
                        if not allow_SUBP:
                            perr("%s param %d cannot have subcodes" % (name, i))
                        # 'commands' is required for SUBP and contains bytecodes
                        elif 'commands' in param:
                            commands = param['commands']
                            for command in commands:
                                check_code_info("cmd %s" % command, commands[command], False)
                            param.pop('commands')
                        else:
                            perr("%s param %d missing 'commands'" % (name, i))
                    param.pop('type')
                else:
                    perr("%s param %d missing 'type'" % (name, i))

                # 'dir' is optional (for now) and must be 'in' or 'out'
                if 'dir' in param:
                    if not param['dir'] in ('in', 'out'):
                        perr("%s param %d 'dir' is not valid ('%s')" % (name, i, param['dir']))
                    param.pop('dir')

                # 'enum' is optional and must be a dictionary
                if 'enum' in param:
                    if not type(param['enum']) is dict:
                        perr("%s param %d 'enum' is not a string" % (name, i))
                    param.pop('enum')

                # any extra keys are not allowed
                for extra in param:
                    perr("%s has extra key '%s' in param %d" % (name, extra, i))
        else:
            perr("%s 'params' is not a list" % name)
        info.pop('params')
    else:
        perr("%s is missing 'params'" % name)

    # 'support' is required and must contain a dictionary of forks
    if 'support' in info:
        for fork in ['official', 'xtended', 'compat']:
            if fork in info['support']:
                if not type(info['support'][fork]) is bool:
                    perr("%s requires bool for '%s'" % (name, fork))
                info['support'].pop(fork)
            else:
                perr("%s is missing '%s' under 'support'" % (name, fork))
        for extra in info['support']:
            perr("%s has unknown key '%s' in 'support" % (name, extra))
        info.pop('support')
    else:
        perr("%s is missing 'support'" % name)

    # No other keys are allowed
    for extra in info:
        perr("%s has unknown key '%s'" % (name, extra))


# Do line-by-line validation for things like trailing whitespace

with open('bytecodes.yml') as f:
    trailing_whitespace = re.compile(' +$')
    tabs = re.compile('\t')
    for num, line in enumerate(f.readlines()):
        # we are not super strict on 80 chars, but if we need to wrap a line,
        # we should wrap to 80 chars
        if len(line) > 89:
            perr("Line %d is over 80 chars" % num)
        if trailing_whitespace.match(line):
            perr("Trailing whitespace on line %d" % num)
        if tabs.match(line):
            perr("Tabs on line %d" % num)

# Read as yaml and validate the data structures

with open('bytecodes.yml') as f:
    data = yaml.load(f, Loader=yaml.CLoader)

opcodes = data['op']
for opcode in opcodes:
    info = opcodes[opcode]
    check_code_info("op %s" % opcode, info, True)

exit(failed)
