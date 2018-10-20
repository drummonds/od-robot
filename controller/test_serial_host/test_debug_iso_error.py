"""
Debug why catalogue.json does not have each with a disc number
"""

from odarchive import Archiver, load_archiver_from_json


def test_get_info():
    # ar = Archiver()
    # ar.create_file_database(Path("Z:\\Home Pictures"))
    # ar.save()
    # ar.convert_to_hash_database(verbose = True)
    # ar.save()
    ar = load_archiver_from_json()
    # start
    # ar.hash_db.save()
    # ar.save()
    #ar.segment("bd")
    #ar.save()
    #ar.hash_db.save()
    print(ar.get_info())
    print(ar.hash_db.get_info())
    # end
    #ar.write_iso(disc_num=0)


if __name__ == "__main__":
    test_get_info()
