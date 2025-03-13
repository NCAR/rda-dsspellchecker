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


if __name__ == "__main__":
    unittest.main(verbosity=2)
