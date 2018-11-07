from collections import OrderedDict
from enum import Enum
import json
from mmap import mmap, ACCESS_READ
from pathlib import Path, PurePosixPath
from os import fsdecode, fsencode, getcwd, lstat, readlink, stat_result, getcwd
from os.path import normpath

try:
    from scandir import walk
except ImportError:
    from os import walk
from stat import S_ISLNK, S_ISREG
from sys import stderr

from .consts import *
from .file_db import FileDatabase
from .file_entry import FileEntryType, FileEntry
from .hash_file_entry import HashFileEntries, HashFileEntry, interpret_disc_capacity


class HashDatabase:

    def __init__(self, file_db: FileDatabase, iso_path_root):
        self.iso_path_root = iso_path_root
        self.db_path = Path(DB_FILENAME)
        self.hash_entries = HashFileEntries.create(self.iso_path_root, file_db.path)
        self.version = DATABASE_VERSION
        self.segment_size = None  # DB is started not segmented
        self.last_disc_number = None  # This starts as a non segmented archive
        self.update(file_db)

    def save(self, catalogue_name=DB_FILENAME):
        """Save the current catalogue to file as a JSON file.
        It should be possible to reread this file later and recreate this record."""
        filename = Path(getcwd()) / catalogue_name
        data = {
            # Todo If use original path then need to create dynamically the path to match
            # "OriginalPath": str(self.path),
            "version": self.version,
            "files": json.loads(self.hash_entries.to_json()),
            # List of directories are derived from file paths
            # List of catalogues as GUID, the first will be this catalogue
        }
        with filename.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)

    def segment(self, size, catalogue_size):
        """
        For a catalogue will place each file onto a disc.
        This will overwrite the segments if carrie out repeatedly.
        :param size:
        :return:
        """
        self.str_catalogue_size = size
        new_size = interpret_disc_capacity(size)
        self.int_catalogue_size = new_size
        self.segment_size = new_size
        OVERHEAD = (
            500000 + catalogue_size
        )  # This is the number of bytes of overhead that will be used for size of iso file
        # TODO needs a method to deal more accruately with directory sizes
        FILE_OVERHEAD = (
            2048
        )  # This is the number of bytes of overhead this is allocated for each file in addition
        # to the actual contents of the file.  Needs to cover directory entries.
        min_size = OVERHEAD + FILE_OVERHEAD + next(iter(self.files())).size
        if new_size <= min_size:
            raise PyArchiveError(f"Disc too small {new_size:,}, cannot fit first file on with overhead {min_size:,}.")

        count = OVERHEAD # Count the number of bytes used
        self.last_disc_number = 0
        for entry in self.files():
            size_on_disc = (
                (2048 + entry.size) // 2048
            ) * 2048 + FILE_OVERHEAD
            if (count + size_on_disc) >= self.segment_size:
                # If too big to fit file in segment then start a new disc
                count = OVERHEAD
                self.last_disc_number += 1
            # Only add
            entry.disc_num = self.last_disc_number
            count += size_on_disc
            if count > self.segment_size:
                # if file is too big to fit on a single disc with overhad
                raise PyArchiveError(f"Disc too small {new_size:,}, cannot fit file {entry.filename} on disc {self.last_disc_number} with overhead {count:,}.")

    @property
    def is_segmented(self):
        return self.last_disc_number is not None

    def _find_changes(self):
        """
        Walks the filesystem. Identifies noteworthy files -- those
        that were added, removed, or changed (size, mtime or type).

        Returns a 3-tuple of sets of FileEntry objects:
        [0] added files
        [1] removed files
        [2] modified files

        self.entries is not modified; this method only reports changes.
                Should make parallel like this
        from joblib import Parallel, delayed
	import multiprocessing
	# what are your inputs, and what operation do you want to
	# perform on each input. For example...
	inputs = range(10)
	def processInput(i):
	    return i * i

	num_cores = multiprocessing.cpu_count()

	results = Parallel(n_jobs=num_cores)(delayed(processInput)(i) for i in inputs)

	from https://blog.dominodatalab.com/simple-parallelization/

        Returns the number of file hashes imported.

        """
        added = set()
        modified = set()
        existing_files = set()
        for dirpath_str, _, filenames in walk(str(self.path)):
            dirpath = Path(dirpath_str)
            for filename in filenames:
                # Make the assumption the database is never in the path
                abs_filename = (dirpath / filename).absolute()
                if abs_filename in self.file_entries:
                    entry = self.file_entries[abs_filename]
                    existing_files.add(entry)
                    st = lstat(str(abs_filename))
                    if entry != st:
                        modified.add(entry)
                else:
                    entry = FileEntry(self, abs_filename)
                    entry.update_attrs()
                    added.add(entry)
        removed = set(self.file_entries.values()) - existing_files
        return added, removed, modified

    def update(self, file_db):
        """
        Iterates a file entry database to get each entry and add to hash database
        """
        for entry in file_db.files():
            self.hash_entries.add_hash_file(entry)

    def files(self, disc_num=None):
        for entry in self.hash_entries.values():
            if disc_num is None:  # without a disc num specification return all files
                yield entry
            elif entry.disc_num == disc_num:  # only get entries for this disc_num
                yield entry

    def get_info(self, for_disc_num = None):
        """Returns summary information on archive"""
        count_files = 0
        size_files = 0
        disc_nums = set()
        entries_no_disc = 0
        largest_file = 0
        for entry in self.files():
            if for_disc_num is None or entry.disc_num is None or for_disc_num == entry.disc_num:
                count_files += 1
                size_files += entry.size
                if self.is_segmented:
                    if entry.disc_num is None:
                        entries_no_disc += 1
                    else:
                        disc_nums |= {entry.disc_num}
                if entry.size > largest_file:
                    largest_file = entry.size
        max_length = 0
        longest_dir = ""
        dirs = set()
        for this_dir in self.hash_entries.dir_entries():
            dirs = dirs | {this_dir}
            length = len(Path(this_dir).parts) - 1
            if length > max_length:
                longest_dir = this_dir
                max_length = length
        result = ""
        if for_disc_num is not None:
            result += f'/n>>>>>>>>> Disc {for_disc_num} <<<<<<<<<<<<<<<<\n'
        result += f"Number of files = {count_files:,}\n"
        result += f"  Largest file  = {largest_file:,}\n"
        result += f"Data size       = {size_files:,}\n"
        result += f"Is segmented    = {self.is_segmented}\n"
        if self.is_segmented:  # Add information about disc size
            if isinstance(self.str_catalogue_size, str):  # Then can interpret text
                result += (
                    f"  Disc = {self.str_catalogue_size}, segment size = {self.int_catalogue_size:,} bytes\n"
                )
            else:  # Can only write size
                result += f"  Disc segment size = {self.int_catalogue_size:,} bytes\n"
            result += f"  Number of discs = {self.last_disc_number+1:,}\n"
        if entries_no_disc > 0 and self.is_segmented:
            result += (
                f"  {entries_no_disc} entries have not been allocated a disc number and should have been.\n"
            )
        result += f"Number of dirs  = {len(dirs)}\n"
        result += f"Max dir depth   = {max_length} (on ISO UDF file system)\n"
        result += f" Dir =: {longest_dir}\n"
        return result

    def __len__(self):
        return len(self.hash_entries)

