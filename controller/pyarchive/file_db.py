"""This is a file database.  It is centred on the file system but can do things like estimate the number of
segments.  The is NO HASHING and hasing inverts the database and then correlates to the UDF file format
on discs.
This is a temporary structure and although can be preserved by pickle is not intended to have a long duration.
So it does not need versioning.
"""
from collections import OrderedDict
from pathlib import Path, PurePosixPath
from os import fsdecode, fsencode, getcwd, lstat, readlink, stat_result, getcwd
from scandir import walk
from sys import stderr

from .consts import *
from .hash_file_entry import interpret_disc_capacity
from .file_entry import FileEntry

from multiprocessing import Process, Queue
from math import sqrt
from joblib import Parallel, delayed
from multiprocessing import Process, Queue, cpu_count


def do_hash(entry):
    """Make an easy parallel task"""
    entry.calculate_file_hash()


class FileDatabase:

    def __init__(self, path: Path):
        self.path = path.absolute()
        self.file_entries = OrderedDict()  # of FileEntry
        self.segment_size = None  # DB is started not segmented
        self.last_disc_number = None  # This starts as a non segmented archive

    def segment(self, size, catalogue_size=0):
        """
        For a catalogue will place each file onto a disc.  Note this is approximate as it does not cover
        de duplication.

        :param size: This is a text string eg 'cd' or size in bytes eg 737000000 of the max size of the segment
        :param catalogue_size: Every disc has a catalogue on it for the whole disc so this is the size of that cataloge
        :return:
        """
        self.str_catalogue_size = size
        new_size = interpret_disc_capacity(size)
        self.int_catalogue_size = new_size
        if not self.segment_size:
            self.segment_size = new_size
        elif self.segment_size != new_size:
            raise PyArchiveError(
                f"New size ({new_size}) is not same as size already in archive ({self.segment_size})"
            )
        OVERHEAD = (
            500000 + catalogue_size
        )  # This is the number of bytes of overhead that will be used for size of iso file
        # TODO needs a method to deal more accruately with directory sizes
        FILE_OVERHEAD = (
            2048
        )  # This is the number of bytes of overhead this is allocated for each file in addition
        # to the actual contents of the file.  Needs to cover directory entries.

        count = OVERHEAD  # Count the number of bytes used
        if self.last_disc_number:
            self.last_disc_number += 1
        else:
            self.last_disc_number = 0
        for entry in self.files():
            if (
                entry.disc_num is None
            ):  # Only add to segment entries that have not already been added
                # This allows the command to be rerun happily
                entry.disc_num = self.last_disc_number
                count += (
                    (2048 + entry.size) // 2048
                ) * 2048 + FILE_OVERHEAD  # Only whole sectors are allocated.
                if count >= self.segment_size:
                    count = OVERHEAD
                    self.last_disc_number += 1

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

    def update(self, this_path=None):
        """
        Walks the filesystem, adding and removing files from
        the database as appropriate.

        Returns a 3-tuple of sets of filenames:
        [0] added files
        [1] removed files
        [2] modified files
        """
        if this_path is None:
            this_path = self.path
        added, removed, modified = self._find_changes()
        for entry in added:
            entry.update()  # Calculate hash
            self.file_entries[entry.filename] = entry
        for entry in removed:
            del self.file_entries[entry.filename]
        # Entries will appear in 'modified' if the size, mtime or type
        # change. This will not be reliable over time (you need hashes to do that)
        # I've seen a lot of spurious mtime mismatches on vfat
        # filesystems (like on USB flash drives), so only report files
        # as modified if the hash changes.
        content_modified = set()
        for entry in modified:
            old_entry = entry
            entry.update()
            if entry != old_entry:
                content_modified.add(entry)
        return (
            {entry.filename for entry in added},
            {entry.filename for entry in removed},
            {entry.filename for entry in content_modified},
        )

    def status(self):
        added, removed, modified = self._find_changes()
        return (
            {entry.filename for entry in added},
            {entry.filename for entry in removed},
            {entry.filename for entry in modified},
        )

    def verify(self, verbose_failures=False):
        """
        Calls each FileEntry's verify method to make sure that
        nothing has changed on disk.

        Returns a 2-tuple of sets of filenames:
        [0] modified files
        [1] removed files
        """
        modified = set()
        removed = set()
        count = len(self.entries)
        # TODO: Track number of bytes hashed instead of number of files
        # This will act as a more meaningful progress indicator
        i = 0
        for i, entry in enumerate(self.entries.values(), 1):
            if entry.exists():
                if entry.verify():
                    entry.update_attrs()
                else:
                    if verbose_failures:
                        stderr.write(
                            "\r{} failed hash verification\n".format(entry.filename)
                        )
                    modified.add(entry.filename)
            else:
                removed.add(entry.filename)
                if verbose_failures:
                    stderr.write("\r{} is missing\n".format(entry.filename))
            stderr.write("\rChecked {} of {} files".format(i, count))
        if i:
            stderr.write("\n")
        return modified, removed

    def file_paths(self):
        for entry in self.file_entries.values():
            yield str(entry.relative_path)

    def files(self, disc_num=None):
        for entry in self.file_entries.values():
            if disc_num is None:  # without a disc num specification return all files
                yield entry
            elif entry.disc_num == disc_num:  # only get entries for this disc_num
                yield entry

    def print_files(self):
        for entry in self.file_entries.values():
            print(entry)

    def __len__(self):
        return len(self.file_entries)

    def get_info(self):
        """Returns summary information on archive"""
        count_files = 0
        size_files = 0
        disc_nums = set()
        entries_no_disc = 0
        for entry in self.files():
            count_files += 1
            size_files += entry.size
            if self.is_segmented:
                if entry.disc_num is None:
                    entries_no_disc += 1
                else:
                    disc_nums |= {entry.disc_num}
        max_length = 0
        longest_dir = ""
        dirs = set()
        for this_dir in self.file_entries:
            dirs = dirs | {this_dir.parent}
            length = len(Path(this_dir).parts) - 2
            if length > max_length:
                longest_dir = this_dir.parent
                max_length = length
        result = ""
        result += f"Number of files = {count_files:,}\n"
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
        result += f"Max dir depth   = {max_length} (on source file system)\n"
        result += f" Dir =: {longest_dir}\n"
        return result

    # Single Threaded version
    def calculate_file_hash(self, verbose=False):
        count = 0
        for entry in self.file_entries.values():
            entry.calculate_file_hash()
            count += 1
            if verbose:
                if (count % 1000) == 0:
                    print(f" {count}", flush=True)
                elif (count % 10) == 0:
                    print('.', end='', flush=True)
        if verbose and not ((count % 1000) == 0):  # Close off line if part finished
            print(f" {count}", flush=True)

    # Multithreaded version
    def p_calculate_file_hash(self, verbose=False):
        """This is a simple version where the whole input queue is built, then processed in parallel to a results queue
        and then back in a single process the results queue is processed"""
        Parallel(n_jobs=2)(delayed(do_hash)(entry) for entry in self.file_entries.values())

