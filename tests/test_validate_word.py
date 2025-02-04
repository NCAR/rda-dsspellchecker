import unittest


from dsspellchecker import SpellChecker
from dsspellchecker.utils import validate_word


class TestCheckWord(unittest.TestCase):
    def test_number(self):
        self.assertFalse(validate_word("#1", None))
        self.assertTrue(validate_word("#1.1", None))
        self.assertFalse(validate_word("#313", None))


    def test_int_float_currency(self):
        self.assertFalse(validate_word("100738", None))
        self.assertFalse(validate_word("307.957", None))
        self.assertFalse(validate_word("307.957.2888", None))
        self.assertFalse(validate_word("-307.957", None))
        self.assertFalse(validate_word("$2,007.15", None))
        self.assertFalse(validate_word("($2,007.15)", None))


    def test_ratio_fraction_date(self):
        self.assertFalse(validate_word("9:3", None))
        self.assertFalse(validate_word("9/3", None))
        self.assertFalse(validate_word("9/3/2005", None))
        self.assertTrue(validate_word("14/9/3/2005", None))


    def test_decade(self):
        self.assertFalse(validate_word("1900s", None))
        self.assertFalse(validate_word("400s", None))
        self.assertFalse(validate_word("20s", None))


    def test_ordinal(self):
        self.assertFalse(validate_word("21st", None))
        self.assertFalse(validate_word("3rd", None))
        self.assertFalse(validate_word("94th", None))
        self.assertFalse(validate_word("52nd", None))


    def test_dataset_id(self):
        self.assertFalse(validate_word("d083002", None))
        self.assertTrue(validate_word("ds083.2", None))


    def test_pre_number(self):
        self.assertFalse(validate_word("pre-1950", None))
        self.assertTrue(validate_word("pre-industrial", None))


    def test_version(self):
        self.assertFalse(validate_word("v2.0", None))
        self.assertFalse(validate_word("v2.0.7.5", None))
        self.assertFalse(validate_word("0.x", None))
        self.assertTrue(validate_word("0.y", None))
        self.assertFalse(validate_word("1a", None))
        self.assertFalse(validate_word("14B", None))


    def test_ncartechnote(self):
        self.assertFalse(validate_word("NCAR/TN-477+STR", None))


    def test_itemization(self):
        self.assertFalse(validate_word("a.", None))
        self.assertFalse(validate_word("1.", None))
        self.assertFalse(validate_word("B.", None))
        self.assertTrue(validate_word("B2.", None))


    def test_reference(self):
        self.assertFalse(validate_word("(a)", None))
        self.assertFalse(validate_word("(9)", None))
        self.assertFalse(validate_word("(10)", None))
        self.assertFalse(validate_word("(A5D)", None))
        self.assertTrue(validate_word("(A5D1)", None))
        self.assertFalse(validate_word("(iii)", None))
        self.assertFalse(validate_word("(viii)", None))
        self.assertFalse(validate_word("(xxxviii)", None))
        self.assertTrue(validate_word("(xlviii)", None))


    def test_email_address(self):
        self.assertFalse(validate_word("joe.schmo@gmail.com", None))
        self.assertFalse(validate_word("joe.schmo@srv1.gmail.com", None))
        self.assertTrue(validate_word("a@b.c", None))


    def test_file_extension(self):
        self.assertFalse(validate_word(".text", None))
        self.assertTrue(validate_word(".myextension", None))
        self.assertFalse(validate_word(".grib1", None))


    def test_filename(self):
        sc = SpellChecker()
        self.assertFalse(validate_word("test.nc", sc._file_ext_valids))
        self.assertTrue(validate_word("test.nc7", sc._file_ext_valids))
        self.assertFalse(validate_word("test.grb", sc._file_ext_valids))
        self.assertFalse(validate_word("test.h5", sc._file_ext_valids))


    def test_url(self):
        self.assertFalse(validate_word("http://rda.ucar.edu", None))
        self.assertFalse(validate_word("https://rda.ucar.edu", None))
        self.assertFalse(validate_word("ftp://rda.ucar.edu", None))
        self.assertFalse(validate_word("mailto:rda.ucar.edu", None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
