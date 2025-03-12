import unittest


from dsspellchecker import SpellChecker
from dsspellchecker.utils import ignore_word


class TestCheckWord(unittest.TestCase):
    def test_number(self):
        self.assertTrue(ignore_word("#1", None))
        self.assertFalse(ignore_word("#1.1", None))
        self.assertTrue(ignore_word("#313", None))


    def test_int_float_currency(self):
        self.assertTrue(ignore_word("100738", None))
        self.assertTrue(ignore_word("307.957", None))
        self.assertTrue(ignore_word("307.957.2888", None))
        self.assertTrue(ignore_word("-307.957", None))
        self.assertTrue(ignore_word("$2,007.15", None))
        self.assertTrue(ignore_word("($2,007.15)", None))


    def test_ratio_fraction_date(self):
        self.assertTrue(ignore_word("9:3", None))
        self.assertTrue(ignore_word("9/3", None))
        self.assertTrue(ignore_word("9/3/2005", None))
        self.assertFalse(ignore_word("14/9/3/2005", None))


    def test_decade(self):
        self.assertTrue(ignore_word("1900s", None))
        self.assertTrue(ignore_word("400s", None))
        self.assertTrue(ignore_word("20s", None))


    def test_ordinal(self):
        self.assertTrue(ignore_word("21st", None))
        self.assertTrue(ignore_word("3rd", None))
        self.assertTrue(ignore_word("94th", None))
        self.assertTrue(ignore_word("52nd", None))


    def test_dataset_id(self):
        self.assertTrue(ignore_word("d083002", None))
        self.assertFalse(ignore_word("ds083.2", None))


    def test_pre_number(self):
        self.assertTrue(ignore_word("pre-1950", None))
        self.assertFalse(ignore_word("pre-industrial", None))


    def test_version(self):
        self.assertTrue(ignore_word("v2.0", None))
        self.assertTrue(ignore_word("v2.0.7.5", None))
        self.assertTrue(ignore_word("0.x", None))
        self.assertFalse(ignore_word("0.y", None))
        self.assertTrue(ignore_word("1a", None))
        self.assertTrue(ignore_word("14B", None))


    def test_ncartechnote(self):
        self.assertTrue(ignore_word("NCAR/TN-477+STR", None))


    def test_itemization(self):
        self.assertTrue(ignore_word("a.", None))
        self.assertTrue(ignore_word("1.", None))
        self.assertTrue(ignore_word("B.", None))
        self.assertFalse(ignore_word("B2.", None))


    def test_reference(self):
        self.assertTrue(ignore_word("(a)", None))
        self.assertTrue(ignore_word("(9)", None))
        self.assertTrue(ignore_word("(10)", None))
        self.assertTrue(ignore_word("(A5D)", None))
        self.assertFalse(ignore_word("(A5D1)", None))
        self.assertTrue(ignore_word("(iii)", None))
        self.assertTrue(ignore_word("(viii)", None))
        self.assertTrue(ignore_word("(xxxviii)", None))
        self.assertFalse(ignore_word("(xlviii)", None))


    def test_email_address(self):
        self.assertTrue(ignore_word("joe.schmo@gmail.com", None))
        self.assertTrue(ignore_word("joe.schmo@srv1.gmail.com", None))
        self.assertFalse(ignore_word("a@b.c", None))


    def test_file_extension(self):
        self.assertTrue(ignore_word(".text", None))
        self.assertFalse(ignore_word(".myextension", None))
        self.assertTrue(ignore_word(".grib1", None))


    def test_filename(self):
        sc = SpellChecker()
        self.assertTrue(ignore_word("test.nc", sc._file_ext_valids))
        self.assertFalse(ignore_word("test.nc7", sc._file_ext_valids))
        self.assertTrue(ignore_word("test.grb", sc._file_ext_valids))
        self.assertTrue(ignore_word("test.h5", sc._file_ext_valids))


    def test_url(self):
        self.assertTrue(ignore_word("http://rda.ucar.edu", None))
        self.assertTrue(ignore_word("https://rda.ucar.edu", None))
        self.assertTrue(ignore_word("ftp://rda.ucar.edu", None))
        self.assertTrue(ignore_word("mailto:rda.ucar.edu", None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
