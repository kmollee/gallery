#!/usr/bin/env python

import os
import sys
from string import Template

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LOCAL_SETTINGS_FILE = 'gallery/settings/local.py'
LOCAL_SETTINGS_TEMPLATE = 'gallery/settings/local.template'

settings = { 'secret_key': '', 'domain_name': '', 'admin_name': '',
    'admin_email': '', 'database_engine': '', 'database_name': '',
    'database_user': '', 'database_pass': '', 'database_host': '',
    'database_port': '',
}

def prompt_freeform(prompt, required=True):
    input_var = ''
    show_input = True
    while show_input:
        input_var = input('%s: ' % prompt)
        if input_var == '' and required:
            show_input = True
        else:
            show_input = False
    return input_var

def prompt_from_list(prompt, list):
    input_var = ''
    while input_var not in list:
        input_var = input('%s (%s): ' % (prompt, '/'.join(list)))
    return input_var

if os.path.isfile(LOCAL_SETTINGS_FILE):
    print('It looks like a %s file already exists.' % LOCAL_SETTINGS_FILE)
    print('That could indicate that you have already installed this project.')
    continue_install = prompt_from_list('Continue?', ['y', 'n'])
    if continue_install == 'n':
        sys.exit()

# Overall Settings
settings['secret_key'] = prompt_freeform('Secret Key')
settings['domain_name'] = prompt_freeform('Domain Name')

# Admin Settings
settings['admin_name'] = prompt_freeform('Admin Name', False)
settings['admin_email'] = prompt_freeform('Admin Email', False)

# Database Settings
settings['database_engine'] = prompt_from_list('Database Engine',
    ['mysql', 'oracle', 'postgresql_psycopg2', 'sqlite3'])
settings['database_name'] = prompt_freeform('Database Name')
if settings['database_engine'] != 'sqlite3':
    settings['database_host'] = prompt_freeform('Database Host', False)
    settings['database_user'] = prompt_freeform('Database User', False)
    settings['database_pass'] = prompt_freeform('Database Password', False)
    settings['database_port'] = prompt_freeform('Database Port', False)

template = Template(open(LOCAL_SETTINGS_TEMPLATE, 'r').read())

output = template.safe_substitute(**settings)

print(output) # TODO: write this to LOCAL_SETTINGS_FILE

# TODO: python manage.py syncdb
# TODO: python manage.py migrate
# TODO: python manage.py createsuperuser
