import hashlib
import re

# 1: 'version' field added
# 2: entry 'file_type' field added; symlinks now treated correctly
DATABASE_VERSION = 1
DB_FILENAME = "catalogue.json"

HASH_FUNCTION = hashlib.sha512
# Mostly used for importing from saved hash files
EMPTY_FILE_HASH = (
    "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"
    "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
)

SHA512_HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{128}$")

HASH_FILENAME = "SHA512SUM"


class PyArchiveError(Exception):
    pass
