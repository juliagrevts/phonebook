"""
This module implements class Table, the place for accessing and manipulating
data.
"""

from typing import (
    Callable,
    Generator,
    Optional,
    Union
)

from app.storage import JSONStorage


class Table:
    """
    Represents a table.

    It provides methods for accessing and manipulating documents.
    The ``Table`` class is responsible for creating the storage class instance
    that will store this table's documents in JSON file.

    :param storage: The storage instance to use for this table
    :param name: The table name
    :param path: Where to store the JSON data.
    :param access_mode: mode in which the file is opened (r, r+)
    :type access_mode: str
    """

    def __init__(
        self,
        name: str,
        path: str,
        storage=JSONStorage,
        encoding: Optional[str] = None,
        access_mode: str='r+'
    ) -> None:
        """
        Create a table instance.
        """

        # Prepare the storage
        self._storage = storage(path, encoding, access_mode)
        self._name = name

    def __repr__(self):
        args = [
            'name={}'.format(self._name),
            'storage={}'.format(self._storage)
        ]
        return '<{}>'.format(', '.join(args))

    def insert(self, document: dict) -> None:
        """
        Insert a new dict with data into the JSON file.

        :param document: the dict with data to insert
        :type document: dict
        """

        # Make sure the entry document implements the ``dict`` class
        if not isinstance(document, dict):
            raise ValueError('Document is not a Dict')

        # To access and search records in the storage we wil use IDs
        # That is, each record (dict) will have its own key
        # First, we get the next free ID for the new dict
        doc_id = self._get_next_id()

        # Now, we update the table and add the document
        def inserter(table: dict):

            # Create the dict with document as a value and ID as a key           
            table[doc_id] = document
            index = table["index"]

            # update index with indexable fields
            for field in index:
                f_value = document[field]
                if f_value not in index[field]:
                    index[field][f_value] = []
                index[field][f_value].append(str(doc_id))

        # See below for details on ``Table._insert_table``
        self._insert_table(inserter)

    def _insert_table(self, inserter: Callable[[dict], None]) -> None:
        """
        Perform a table update operation.

        The storage used only allows to read/write the
        complete table data, but not modifying only portions of it. Thus,
        to only update portions of the table data, we first perform a read
        operation, perform the update/insert on the table data and then write
        the updated/inserted data back to the storage.
        """

        documents = self._storage.read()
        if documents is None:
            # The database is empty
            documents = {}
            # Create new 'index' dict for fast searching if doesn't exist
            documents['index'] = {
                'first_name': {},
                'last_name': {}
            }

        # Convert the entries dicts IDs to ``int`` class
        # This is required as the rest of Table expects the entries dict IDs
        # to be an instance of ``int`` but the storage
        # might convert dict keys to strings.
        table = {
            int(doc_id): doc
            for doc_id, doc in documents.items()
            if doc_id != 'index'
        }
        # Add index dict to the table object
        table['index'] = documents['index']

        # Perform the table insert operation
        inserter(table)

        # Convert the entries' IDs back to strings.
        # This is required as JSON storages
        # don't support IDs other than strings.
        documents = {
            str(doc_id): doc
            for doc_id, doc in table.items()
        }

        # Write the newly updated data back to the storage
        self._storage.write(documents)

    def _get_next_id(self) -> int:
        """
        Return the ID for a newly inserted document.
        """
        # Determine the next record ID by finding out the max ID value
        # of the current table documents

        # Read the table documents
        table = self._read_table()

        # If the table is empty, set the initial ID
        if not table:
            next_id = 1
            return next_id

        # Determine the next ID based on the maximum ID that's currently in use
        # Delete  the key 'index'  as not to compare it with ``int``
        del table['index']
        max_id = max(int(i) for i in table.keys())
        next_id = max_id + 1

        return next_id

    def _read_table(self) -> dict[str, dict[str, str]]:
        """
        Read the table data from the  storage.
        """

        # Retrieve the tables from the storage
        table = self._storage.read()
        if table is None:
            # The storage is empty
            return {}
        return table

    def all(self, docs_per_page: int = 5) -> Optional[Generator]:
        """
        Get all documents stored in the table.
        """
        table = self._read_table()

        if not table:
            # The storage is empty
            return None

        # We don't want to show the "index" dict to the user
        del table['index']

        # Find out the max ID value of the current table documents to use it in ``Generator``
        max_id = max(int(i) for i in table)

        # Create list of records dicts
        all_docs = list(table.values())

        # Split the records dicts list into the lists of "docs_per_page" dicts in each
        # Create and return generator to paginate table data to pages
        def paginate(all_docs: list[dict[str, str]], docs_per_page: int) -> Generator:
            for x in range(0, max_id + 1, docs_per_page):
                chunk = all_docs[x: docs_per_page + x]
                if chunk:
                    yield chunk

        return paginate(all_docs, docs_per_page)

    def search_ids(self, fields: dict[str, str]) -> Optional[list[str]]:
        """
        Search in table's index for all documents matching fields conditions.

        :param fields: fields to check against
        :returns: list of documents ids
        """

        # Make sure the entry dict isn't empty
        if not fields:
            # No fields passed
            return None
        
        table = self._read_table()
        index = table['index']
        conditions = [f_value in index[f_name] for f_name, f_value in fields.items()]
        if not all(conditions):
            # no records found, matching all conditions
            return None

        # return documents ids
        doc_ids = set.intersection(
            *[set(index[f_name][f_value]) for f_name, f_value in fields.items()]
        )
        return list(doc_ids)

    def search(self, fields: dict[str, str]) -> Optional[list[dict[str, str]]]:
        """
        Search for all documents matching a 'field' cond.

        :param field: fields to check against
        :returns: list of matching documents
        """

        # Get records ids
        doc_ids = self.search_ids(fields)
        if doc_ids is None:
            # No records found
            return None

        # Read JSON file and return the list od records matching the doc ids
        table = self._read_table()
        docs = [table[doc_id] for doc_id in doc_ids]

        return docs


    def update(
        self,
        fields: dict[str, str],
        update_document: dict
        ) -> Optional[str]:
        """
        Update all matching documents to have a given set of fields.

        :param fields: first_name and/or last_name str to check against
        :param update_document: fields that will be updated in the matching documents
        """

        # Make sure the entry document implements the ``dict`` class
        if not isinstance(update_document, dict):
            raise ValueError('Document is not a Dict')

        # Get the desired records ids
        doc_ids = self.search_ids(fields)
        if doc_ids is None:
            # No records found
            return None

        # Now, we update the table and add the document
        def updater(table: dict[int, dict[str, str]], doc_id):

            # If user wants to update first_name or last_name 
            # we should create new keys in the 'index' dict storing the records indexes 
            # for further search by the new first_name or last_name

            # So we create in the 'index 'dict
            # new key with the first_name if it is subject to update
            index = table['index']
            for field in index:
                if field not in update_document:
                    continue
                f_value = update_document[field]
                if f_value not in index[field]:
                    index[field][f_value] = []
                index[field][f_value].append(str(doc_id))

                # drop old value from index
                old_value = table[int(doc_id)][field]
                idxs_to_drop = index[field][old_value]
                if len(idxs_to_drop) > 1:
                    # drop only one id
                    idxs_to_drop.pop(str(doc_id))
                else:
                    index[field].pop(old_value)

                # Update the data in accordance with the user's request
                # for all records dicts found in table
                for update_field in update_document:
                    table[int(doc_id)][update_field] = update_document[update_field]

        # See below for details on ``Table._update_table``
        self._update_table(updater, doc_ids)

        return 'Saved successfully'


    def _update_table(self, updater: Callable[[dict], None], doc_ids: list[str]):
        """
        Perform a table update operation.

        The storage used only allows to read/write the
        complete table data, but not modifying only portions of it. Thus,
        to only update portions of the table data, we first perform a read
        operation, perform the update on the table data and then write
        the updated data back to the storage.
        """

        documents = self._storage.read()

        # Convert the entries dicts IDs to ``int`` class
        # This is required as the rest of Table expects the entries dict IDs
        # to be an instance of ``int`` but the storage
        # might convert dict keys to strings.
        table = {
            int(doc_id): doc
            for doc_id, doc in documents.items()
            if doc_id != 'index'
        }
        # Add index dict to the table object
        table['index'] = documents['index']

        #Perform tha table update operation
        for doc_id in doc_ids:
            updater(table, doc_id)

        # Convert the entries' IDs back to strings.
        # This is required as JSON storages
        # don't support IDs other than strings
        documents = {
            str(doc_id): doc
            for doc_id, doc in table.items()
        }

        # Write the newly updated data back to the storage
        self._storage.write(documents)
