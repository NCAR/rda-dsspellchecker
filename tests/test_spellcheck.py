import unittest


from dsspellchecker import SpellChecker


sc = SpellChecker()


class TestSpellCheck(unittest.TestCase):
    def test_initialize(self):
        self.assertTrue(sc.ready)

    def test_general(self):
        sc.check("Hello, world!")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("Hello, wrold!")
        self.assertEqual(sc.misspelled_words, ["wrold"])
        sc.check("This is a test, (and I hope it passes)!")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("This dataset covers 1850 - 2010.")
        self.assertEqual(sc.misspelled_words, [])
        sc.check(("This dataset contains temperature; a different dataset "
                  "contains winds"))
        self.assertEqual(sc.misspelled_words, [])

    def test_place(self):
        sc.check("I live in Tennessee.")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("I live in tennessee.")
        self.assertEqual(sc.misspelled_words, ['tennessee'])

    def test_exact(self):
        sc.check("This is an e.g. test!")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("This is an e.g test!")
        self.assertEqual(sc.misspelled_words, ['e.g'])
        sc.check("This is an i.e. test!")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("This is an i.e test!")
        self.assertEqual(sc.misspelled_words, ["i.e"])
        sc.check("This is a test (i.e. a check)!")
        self.assertEqual(sc.misspelled_words, [])
        sc.check(("This dataset contains numerous parameters (e.g., "
                  "temperature, pressure, etc.)."))
        self.assertEqual(sc.misspelled_words, [])

    def test_units(self):
        sc.check("This dataset contains 10 m winds at high (4 km) resolution.")
        self.assertEqual(sc.misspelled_words, [])

    def test_quoted(self):
        sc.check("This is a test of quotedgarbage.")
        self.assertEqual(sc.misspelled_words, ["quotedgarbage"])
        sc.check("This is a test of \"quotedgarbage\".")
        self.assertEqual(sc.misspelled_words, [])

    def test_times(self):
        sc.check("It is 17:05 pm in the evening")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("It is 7 am in the morning")
        self.assertEqual(sc.misspelled_words, [])
        sc.check("It is 7:5 am in the morning")
        self.assertEqual(sc.misspelled_words, ["am"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
