import unittest

from dsspellchecker import SpellChecker
from dsspellchecker.utils import ignore_word


class TestCheckWord(unittest.TestCase):
    def test_number(self):
        self.assertTrue(ignore_word("#1"))
        self.assertFalse(ignore_word("#1.1"))
        self.assertTrue(ignore_word("#313"))

    def test_int_float_currency(self):
        self.assertTrue(ignore_word("100738"))
        self.assertTrue(ignore_word("307.957"))
        self.assertTrue(ignore_word("307.957.2888"))
        self.assertTrue(ignore_word("-307.957"))
        self.assertTrue(ignore_word("$2,007.15"))
        self.assertTrue(ignore_word("($2,007.15)"))

    def test_ratio_fraction_date(self):
        self.assertTrue(ignore_word("9:3"))
        self.assertTrue(ignore_word("9/3"))
        self.assertTrue(ignore_word("9/3/2005"))
        self.assertFalse(ignore_word("14/9/3/2005"))

    def test_decade(self):
        self.assertTrue(ignore_word("1900s"))
        self.assertTrue(ignore_word("400s"))
        self.assertTrue(ignore_word("20s"))

    def test_ordinal(self):
        self.assertTrue(ignore_word("21st"))
        self.assertTrue(ignore_word("3rd"))
        self.assertTrue(ignore_word("94th"))
        self.assertTrue(ignore_word("52nd"))

    def test_dataset_id(self):
        self.assertTrue(ignore_word("d083002"))
        self.assertFalse(ignore_word("ds083.2"))

    def test_pre_number(self):
        self.assertTrue(ignore_word("pre-1950"))
        self.assertFalse(ignore_word("pre-industrial"))

    def test_version(self):
        self.assertTrue(ignore_word("v2.0"))
        self.assertTrue(ignore_word("v2.0.7.5"))
        self.assertTrue(ignore_word("0.x"))
        self.assertFalse(ignore_word("0.y"))
        self.assertTrue(ignore_word("1a"))
        self.assertTrue(ignore_word("14B"))

    def test_ncartechnote(self):
        self.assertTrue(ignore_word("NCAR/TN-477+STR"))

    def test_itemization(self):
        self.assertTrue(ignore_word("a."))
        self.assertTrue(ignore_word("1."))
        self.assertTrue(ignore_word("B."))
        self.assertFalse(ignore_word("B2."))

    def test_reference(self):
        self.assertTrue(ignore_word("(a)"))
        self.assertTrue(ignore_word("(9)"))
        self.assertTrue(ignore_word("(10)"))
        self.assertTrue(ignore_word("(A5D)"))
        self.assertFalse(ignore_word("(A5D1)"))
        self.assertTrue(ignore_word("(iii)"))
        self.assertTrue(ignore_word("(viii)"))
        self.assertTrue(ignore_word("(xxxviii)"))
        self.assertFalse(ignore_word("(xlviii)"))

    def test_email_address(self):
        self.assertTrue(ignore_word("joe.schmo@gmail.com"))
        self.assertTrue(ignore_word("joe.schmo@srv1.gmail.com"))
        self.assertFalse(ignore_word("a@b.c"))

    def test_file_extension(self):
        self.assertTrue(ignore_word(".text"))
        self.assertFalse(ignore_word(".myextension"))
        self.assertTrue(ignore_word(".grib1"))

    def test_filename(self):
        sc = SpellChecker()
        self.assertTrue(ignore_word("test.nc", file_exts=True,
                                    cursor=sc._cursor))
        self.assertFalse(ignore_word("test.nc7", file_exts=True,
                                     cursor=sc._cursor))
        self.assertTrue(ignore_word("test.grb", file_exts=True,
                                    cursor=sc._cursor))
        self.assertTrue(ignore_word("test.h5", file_exts=True,
                                    cursor=sc._cursor))

    def test_url(self):
        self.assertTrue(ignore_word("http://rda.ucar.edu"))
        self.assertTrue(ignore_word("https://rda.ucar.edu"))
        self.assertTrue(ignore_word("ftp://rda.ucar.edu"))
        self.assertTrue(ignore_word("mailto:rda.ucar.edu"))

    def test_general(self):
        self.assertFalse(ignore_word("e.g"))
        self.assertFalse(ignore_word("Tennessee"))
        self.assertFalse(ignore_word("dataset"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
