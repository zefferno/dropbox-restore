dropbox-restore
===============

Most modern Ransomwares include a mechanism which uses a strong encryption to encrypt victim files.
Files with extensions: pdf, xlsx, docx and etc. are main targets for ransomware encryption attack. The keys generated 
for the strong encryption are stored in a remote C&C server, thus makes the recovery process most times almost impossible. In such scenarios, most targets tend to pay ransom to use the decryption service.

This tool utilizes Dropbox recovery (a.k.a "Previous Versions") feature in Dropbox service, to recover files from Dropbox. It automates the necessary steps to recover files from Dropbox.

Usage instructions:
-------------------

To restore the folder "/photos/nyc" to the last available revision, use:

    python restore.py -r /photos/nyc -ext .dlnsvc
    
Note that the path "/photos/nyc" should be relative to your Dropbox folder; it should not include the path to the Dropbox folder on your hard drive. You will be prompted to confirm access to your Dropbox account through the web browser.

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
