"""
Contains the JSONStorage for storing phone book data
"""

import io
import json
import os
from typing import Optional


def touch(path: str) -> None:
    """
    Create a file if it doesn't exist yet.

    :param path: The file to create.
    """
    # Create the file by opening it in 'a' mode which creates the file if it
    # does not exist but does not modify its contents
    with open(path, 'a'):
        pass


class JSONStorage:
    """
    Store the data in a JSON file.
    """

    def __init__(self, path: str, encoding=None, access_mode='r+'):
        """
        Create a new instance.

        Also creates the storage file, if it doesn't exist and the access mode
        is appropriate for writing.

        :param path: Where to store the JSON data.
        :param access_mode: mode in which the file is opened (r, r+)
        :type access_mode: str
        """

        self._mode = access_mode

        # Create the file if it doesn't exist and creating is allowed by the
        # access mode
        if any([character in self._mode for character in ('+', 'w', 'a')]):
            touch(path)

        # Open the file for reading/writing
        self._handle = open(path, mode=self._mode, encoding=encoding)


    def close(self) -> None:
        self._handle.close()


    def read(self) -> Optional[dict[str, dict[str, str]]]:
        # Get the file size by moving the cursor to the file end and reading
        # its location
        self._handle.seek(0, os.SEEK_END)
        size = self._handle.tell()

        if not size:
            # File is empty, so we return ``None`` so Table can properly
            # initialize the database
            return None
        else:
            # Return the cursor to the beginning of the file
            self._handle.seek(0)

            # Load the JSON contents of the file
            return json.load(self._handle)


    def write(self, data: dict[str, dict[str, str]]) -> None:
        # Move the cursor to the beginning of the file just in case
        self._handle.seek(0)

        # Serialize the database state using the user-provided arguments
        serialized = json.dumps(data)

        # Write the serialized data to the file
        try:
            self._handle.write(serialized)
        except io.UnsupportedOperation:
            raise IOError(
                'Cannot write to the phonebook. Access mode is "{0}"'.format(self._mode)
            )

        # Ensure the file has been written
        self._handle.flush()
        os.fsync(self._handle.fileno())

        # Remove data that is behind the new cursor in case the file has
        # gotten shorter
        self._handle.truncate()
