# Phonebook

A simple phone book with CLI, written in pure python.

Implements the following features:

1. Page-by-page output of entries from the phonebook
2. Adding a new entry to the phonebook
3. Update entries in the phonebook
4. Search entries by first name and/or last name

The data is stored in a JSON file.

Requires python3.9+


## Cli Usage

```
python phonebook_cly.py {insert,all,update,search} [-fn FIRST_NAME] [-ln LAST_NAME] [-patr PATRONYMIC] [-pn PERSONAL_NUMBER] [-ofn OFFICE_NUMBER] [-cn COMPANY_NAME] [-sfn SEARCH_FIRST_NAME] [-sln SEARCH_LAST_NAME]
```

The first comand is always 'command', one of the following: 'insert', 'all', 'update', 'search'), a command you want to perform.


Keyword arguments:  
'-fn', '--first_name' should pe passed after "insert" or "update" command

'-ln', '--last_name' should pe passed after "insert" or "update" command

'-patr', '--patronymic' should pe passed after "insert" or "update" command

'-pn', '--personal_number' should pe passed after "insert" or "update" command

'-ofn', '--office_number' should pe passed after "insert" or "update" command

'-cn', '--company_name' should pe passed after "insert" or "update" command

'-sfn', '--search_first_name' should pe passed after "search" or "update" command

'-sln', '--search_last_name' should pe passed after "search" or "update" command


### Usage example

```
# get all records page by page, 30 entries for page by default

python phonebook_cli.py all


# insert new record to the phonebook

python phonebook_cli.py insert -fn Ivan -ln Ivanov -patr Ivanovich -cn Romashka -pn 88000000000 -ofn 89999999999


# search all records by first name and last name

python phonebook_cli.py search -sfn Julia -sln Grevtseva


# search all records by first name and last name and then update, for example, the company name in all records matching a cond

python phonebook_cli.py update -sfn Julia -sln Grevtseva -cn Vasilek

```
