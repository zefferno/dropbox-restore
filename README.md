dropbox-restore
===============

Most modern Ransomwares include a mechanism which uses strong encryption in order to encrypt users files.
Files with extensions: .pdf, .xlsx, .docx and etc. are main targets for ransomware encryption. The key generated 
for the strong decryption is stored somewhere in a remote C&C server and thus makes the recovery process without 
backup almost impossible. In such cases, the only way to decrypt the files is to pay a ransom for the 
decryption service.

This is where this tool comes into play. It fully automates the process of recovering files from Dropbox client 
after that were encrypted and deleted during ransomware activity. In order to recover files it uses
the "Previous Versions" feature of Dropbox service.

Usage instructions:
-------------------

To restore the folder "/photos/nyc" to the last available revision use:

    python restore.py -r /photos/nyc -ext .dlnsvc
    
Note that the path "/photos/nyc" should be relative to your Dropbox folder; it should not include the path to the Dropbox folder on your hard drive. You will be prompted to confirm access to your Dropbox account through your web browser.

General Requirements:
---------------------

- Dropbox client 
- Dropbox Core API SDK for Python

Installation Steps:
-------------------

1. First make sure that Python 3.4 and pip are installed. 
2. Then install the Dropbox Python API with the following command.

    sudo pip install dropbox

3. Download restore.py from Github and place it local directory.

Forking:
--------

If you fork this project, you must obtain your own API keys from Dropbox and insert them into the APP\_KEY and APP\_SECRET fields.
