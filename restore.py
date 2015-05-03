#!/usr/bin/env python
# ----------------------------------------------------------------------------------------------------------------------
# Dropbox ransomware recovery tool
# ----------------------------------------------------------------------------------------------------------------------
# This tool automates the process of recovering files from Dropbox site after that were encrypted and deleted during
# ransomware activity. It uses the previous versions feature of Dropbox.
#
# Most modern ransomwares include a mechanism which uses strong encryption in order to encrypt users files.
# Files with extensions like: .pdf, .xlsx, .docx and etc. are targets for encryption. The key generated for the strong
# decryption is stored at a remote server and thus makes the recovery process without backup almost impossible.
# In such cases, the only way to decrypt the files is to pay a ransom for the decryption service served
# at the criminals website.

__author__ = 'Mor Kalfon (zefferno)'
__version__ = '1.0'
__email__ = 'zefferno@gmail.com'

import sys
import os
import timeit
import dropbox
from argparse import ArgumentParser
from time import sleep
from datetime import datetime


APP_KEY = 'v6j6tteotwt908i'
APP_SECRET = '0cyix1u4fge0ss2'
QUERY_SEC_DELAY = 0.2
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S'
DAYS_BACK = 15
TOKEN_FILE = 'token.dat'
FILE_LIMIT = 25000
REVISIONS_LIMIT = 1000


def connect_dropbox():
    """ Connect to Dropbox account
    :return: DropboxClient instance, none if failed
    """

    def authorization():
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
        authorize_url = flow.start()

        print('Authorization is required!')
        print()
        print('1. Browse to the following URL: ' + authorize_url)
        print('2. Click "Allow" (you might have to log in first).')
        print('3. Copy the authorization code.')
        print()

        code = input('Paste the authorization code here: ')
        access_token, user_id = flow.finish(code.strip())

        return access_token

    # Check if we already have token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as token_file:
            access_token = token_file.read()
    else:
        access_token = authorization()
        with open(TOKEN_FILE, 'w') as token_file:
            token_file.write(access_token)

    # Construct DropboxClient instance
    client = dropbox.client.DropboxClient(access_token)

    return client


def restore_file(client, encrypted_file_path, extensions, up_to_revision_to_restore=1):
    """ Restore file from Dropbox
    :param client: DropboxClient instance
    :param encrypted_file_path: Path to the encrypted file
    :param extensions: Extensions of files identified as encrypted
    :param up_to_revision_to_restore: Optional. Up to this number of recent revisions will be restored.
    :return: restored file metadata
    """

    # Metadata of restored file
    restored_file_metadata = None

    # Extract encrypted file name without extension
    filename = get_file_name(encrypted_file_path)
    # Extract encrypted file path
    path = os.path.dirname(encrypted_file_path)
    # Fetch metadata for file
    metadata = retrieve_metadata(client, path, deleted_files=True)
    # Get file list
    files_list = get_list_from_metadata(metadata, extensions, False, True)

    for file in filter(lambda f: get_file_name(f) == filename, files_list):
        revisions = client.revisions(file, rev_limit=up_to_revision_to_restore)
        if revisions:
            revision_to_restore = revisions.pop()
            print("Restoring: " + file)
            restored_file_metadata = client.restore(file, revision_to_restore['rev'])

    return restored_file_metadata


def scan_files(client, root, extensions, traversal=True):
    """ Encrypted files scanner
    :param client: DropboxClient instance
    :param root: root folder inside Dropbox dir
    :param extensions: Extensions of files identified as encrypted
    :param traversal: Enable or disable directories traversal
    :return: list of paths to encrypted files
    """

    # Fetch path metadata
    metadata = retrieve_metadata(client, root)
    # Get folders list
    folders_list = get_folders_list(metadata)
    # Get files list
    files_list = get_list_from_metadata(metadata, extensions)

    # If directory traversal is required, do recursive call
    if traversal:
        for folder in folders_list:
            # Delay for Dropbox limits
            sleep(QUERY_SEC_DELAY)
            # Update progress on console
            print_progress(folder)
            # add
            files_list.extend(scan_files(client, folder, extensions))

    return files_list


def print_progress(path):
    """ Prints status progress during scan
    :param path: Path of scanned file
    """

    line = 'Scanning [{0}] for encrypted files...'.format(path)
    sys.stdout.write(line + (os.get_terminal_size().columns - 1 - len(line)) * ' ' + '\r')
    sys.stdout.flush()


def print_scan_summary(start_time, encrypted_count=0, restored_count=0):
    """ Prints scan summary
    :param start_time: Sample of time before running the scan
    :param encrypted_count: Number of encrypted files found
    :return:
    """

    elapsed = timeit.default_timer() - start_time

    print('\nScan completed successfully.')
    print('\nSummary:')
    print('-' * 40)

    if encrypted_count > 0:
        print('Total encrypted files: ' + str(encrypted_count))

    if restored_count > 0:
        print('Total restored files: ' + str(restored_count))

    print('Scan took %.1f minute(s).' % (elapsed / 60))


def print_logo():
    """ Prints the logo """
    print('+' + '-' * 48 + '+')
    print('| Dropbox ransomware recovery tool v' + __version__ + ' ' * 10 + '|')
    print('|' + '-' * 48 + '|')
    print('| Author: ' + __author__ + ' ' * 18 + '|')
    print('+' + '-' * 48 + '+')
    print()


def get_file_extension(path):
    """ Get filename extension from full path
    :param path: Full path to file
    :return: File extension
    """

    return os.path.splitext(os.path.basename(path))[1]


def get_file_name(path):
    """ Get filename from full path
    :param path: Full path to file
    :return: Filename
    """
    return os.path.splitext(os.path.basename(path))[0]


def get_last_directory(path):
    """ Get the last directory from full path
    :param path: Full path
    :return: Last directory
    """

    return os.path.basename(os.path.dirname(path))


def get_folders_list(metadata):
    """ Get folders list from DropboxClient metadata
    :param metadata: DropboxClient metadata
    :return: List of folders
    """

    folders_list = []

    for dir_item in filter(lambda f: f.get('is_dir'), metadata['contents']):
        folders_list.append(dir_item['path'])

    return folders_list


def get_list_from_metadata(metadata, extensions, include_ext=True, include_deleted=False):
    """ Get files list from DropboxClient metadata
    :param metadata: DropboxClient metadata
    :param extensions: Extensions of files identified as encrypted
    :param include_ext: Optional. Include/Exclude extensions from search
    :param include_deleted: Include/Exclude deleted files
    :return: List of files
    """

    files_list = []
    deleted = False

    for file_item in filter(lambda f: not f.get('is_dir'), metadata['contents']):
        if 'is_deleted' in file_item:
            deleted = file_item['is_deleted']

        ext_included = get_file_extension(file_item['path']) in extensions

        if include_deleted == deleted and include_ext == ext_included:
            files_list.append(file_item['path'])

    return files_list


def parse_date(string):
    """ Parse the string according to the datetime format of the core API
    :param string: String to parse
    :return: Parsed datetime format
    """

    return datetime.strptime(string.split('+')[0].strip(), DATE_FORMAT)


def retrieve_metadata(client, path, deleted_files=False, file_limits=FILE_LIMIT):
    """
    :param client: DropboxClient instance
    :param path: Path inside Dropbox account
    :param deleted_files: True if deleted files should be included in the query, or False otherwise
    :param file_limits: Optional. Set files limit for the query
    :return:
    """

    try:
        #normalize('NFC', string).encode('utf-8')
        metadata = client.metadata(path, include_deleted=deleted_files, file_limit=file_limits)
    except dropbox.rest.ErrorResponse as e:
        print('Dropbox Exception: ' + str(e))
        return []

    return metadata



def main():
    print_logo()

    # Arguments parsing
    parser = ArgumentParser()
    parser.add_argument('-ext', '--extension', nargs='+', required=True, type=str, dest='ext',
                        help='File extension identified as encrypted by the ransomware. '
                             'Multiply extensions can be specified.')
    parser.add_argument('-r', '--root', required=True, type=str, dest='scan_root',
                        help='Root directory to start the scan from.')
    parser.add_argument('-d', '--destination', type=str, dest='destination',
                        help='Destination directory where to place recovered files.')
    parser.add_argument('-re', '--revision', type=int, dest='revision', choices=range(1, FILE_LIMIT),
                        metavar='[1-%s]' % FILE_LIMIT, help='Previous revision to restore.')
    parser.add_argument('-de', '--delete-encrypted', dest='delete_encrypted', action='store_false',
                        help='Delete encrypted files after successful restore.')
    parser.add_argument('-t', '--test', dest='test', action='store_true',
                        help='Test mode. Do not make changes, just print intentions to screen.')

    args = parser.parse_args()

    # Authorize script to access the Dropbox Core API
    client = connect_dropbox()

    # Measure time for summary
    start_time = timeit.default_timer()

    # Discover encrypted files
    encrypted_file_listing = scan_files(client, args.scan_root, args.ext)

    # Restore discovered files
    for file in encrypted_file_listing:
        restore_file(client, file, args.ext)

    print_scan_summary(start_time, len(encrypted_file_listing))

if __name__ == '__main__':
    main()
