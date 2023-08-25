"""
This module implements the CLI for accessing, inserting, searching and updating tha
data in the phonebook.
"""

from argparse import ArgumentParser
from typing import Union

from app.storage import JSONStorage
from app.table import Table


cli = ArgumentParser(
    prog='phonebook',
    description='A phone book that implements the following functionality: '
        '1. Page-by-page output of the phone book entries to the screen; '
        '2. Adding a new entry to the phone book; '
        '3. Ability to edit entries in the phone book; '
        '4. Search for records by first name or by last name or '
        'simultaneously by first name and last name.'
)
"""
Create an ArgumentParser instance and add arguments for parcing.
"""

# Add positional argument 'comand', it should be passed in all cases
# It should be chosen from the available options
cli.add_argument(
    'command',
    choices=['insert', 'all', 'update', 'search'],
    help='provide a command you want to execute from 4 options'
)

# This argument should be passed when executing the insert or update commands
cli.add_argument(
    '-fn', '--first_name',
    help='if command is "insert" or "update" this option allows '
    'to provide a first name to enter or update it in the phone book '
)

# This argument should be passed when executing the insert or update commands
cli.add_argument(
    '-ln', '--last_name',
    help='if command is "insert" or "update" this option allows '
    'to provide a last name to enter or update it in the phone book '
)

# This argument should be passed when executing the insert or update commands
cli.add_argument(
    '-patr', '--patronymic',
    help='if command is "insert" or "update" this option allows '
    'to provide a patronymic to enter or update it in the phone book '
)

# This argument should be passed when executing the insert or update commands
cli.add_argument(
    '-pn', '--personal_number',
    help='if command is "insert" or "update" this option allows '
    'to provide a personal number to enter or update it in the phone book '
)

# This argument should be passed when executing the insert or update commands
cli.add_argument(
    '-ofn', '--office_number',
    help='if command is "insert" or "update" this option allows '
    'to provide an office number to enter or update it in the phone book '
)

# This argument should be passed when executing the insert or update commands
cli.add_argument(
    '-cn', '--company_name',
    help='if command is "insert" or "update" this option allows '
    'to provide a company name to enter or update it in the phone book '
)

# This argument should be passed when executing the search or update commands
cli.add_argument(
    '-sfn', '--search_first_name',
    help='if command is "search" or "update" this option allows '
    'to provide a first name to search the entry by first name'
)

# This argument should be passed when executing the search or update commands
cli.add_argument(
    '-sln', '--search_last_name',
    help='if command is "search" or "update" this option allows '
    'to provide a last name to search the entry by last name'
)


args = vars(cli.parse_args())


# Initialize a new Table instance for accessing to the phonebook and manipulating data
phone_book = Table('phone_book', 'phonebook.json', JSONStorage)


def dict_to_search(args):
    fields_to_search = {}
    if args['search_first_name'] is not None:
        fields_to_search['first_name'] = args['search_first_name']     
    if args['search_last_name'] is not None:
        fields_to_search['last_name'] = args['search_last_name']
    return fields_to_search


# Perform an 'insert' comand
if args['command'] == 'insert':

    # Leave 'insert' fields only
    del args['command']
    del args['search_first_name']
    del args['search_last_name']

    #Insert records
    phone_book.insert(args)
    print('Saved successfully')

# Perform an 'all' command
elif args['command'] == 'all':

    #Get `Generator` object with pagination of JSON file data to 'pages' 
    pages = phone_book.all()

    if pages:
        ans_next = 'y'
        # Show next page until the user says no
        while ans_next == 'y' and pages:
            try:
                print(*next(pages))
                ans_next = input('Next page? (y/n) ')
            except StopIteration:
                print('It was the last page')
                break
    else:
        print('Phonebook is empty')

# Perform a 'search' comand
elif args['command'] == 'search':
    fields_to_search = dict_to_search(args)
    result = phone_book.search(fields_to_search)
    if not result:
        print('No entries matching the criteria')
    else:
        print(*result)

# Perform an 'update' comand
elif args['command'] == 'update':
    fields_to_search = dict_to_search(args)

    # Leave 'update' fields only without None fields and excessive fields
    del args['command']
    del args['search_first_name']
    del args['search_last_name']

    dct_to_update = {
        key: value for key, value in args.items() if value is not None
    }

    # Perform an update operation
    result = phone_book.update(fields_to_search, update_document=dct_to_update)
    if result is None:
        print('No entries matching the criteria')
    else:
        print(result)
 