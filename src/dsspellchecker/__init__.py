import os
import sqlite3

import importlib.metadata

from libpkg.strutils import strip_plural, strip_punctuation

from .db_utils import db_config
from .utils import clean_word, unknown


__version__ = importlib.metadata.version(__package__ or __name__)


class SpellChecker:
    def __init__(self):
        self._misspelled_words = []
        self._error = ""
        try:
            self._conn = sqlite3.connect(
                    os.path.join(os.path.dirname(__file__),
                                 "dictionary/valids.db"))
            #self._conn.set_trace_callback(print)
            self._cursor = self._conn.cursor()
            self._ready = True
            for key in db_config:
                self._cursor.execute("select count(*) from " + key)
                res = self._cursor.fetchall()
                if res[0] == 0:
                    self._ready = False
                    self._error = "Did you build the database?"
                    break

        except Exception as err:
            self._ready = False
            self._error = str(err)

    def __del__(self):
        self._conn.close()

    @property
    def ready(self):
        return self._ready

    @property
    def error(self):
        return self._error

    @property
    def misspelled_words(self):
        return self._misspelled_words

    def check(self, text):
        if not self._ready:
            self._misspelled_words = ["SpellChecker error: '" + self._error +
                                      "'"]
            return

        check_text = text
        check_text = check_text.replace(
                                    "\n", " "
                                ).replace(
                                    "\u2010", "-"
                                ).strip()

        # check the text against the general words with no word cleaning to
        # eliminate as many common words as possible
        self._misspelled_words = (
                unknown(check_text, "general", self._cursor, file_exts=True,
                        cleanWord=False))
        if self._misspelled_words:
            check_text = self.new_text(check_text)
            self._misspelled_words = (
                    unknown(check_text, "non_english", self._cursor,
                            file_exts=True, cleanWord=False))

        if self._misspelled_words:
            exact_matches = {'places', 'names', 'exact_others', 'acronyms'}

            # check the text directly against the exact match valids with
            # no word cleaning because cleaning removes punctuation that might
            # be in an exact match
            check_text = self.new_text(check_text)
            for lstname in exact_matches:
                if self._misspelled_words:
                    self._misspelled_words = (
                            unknown(check_text, lstname, self._cursor,
                                    cleanWord=False, separator="/"))
                    if self._misspelled_words:
                        check_text = self.new_text(check_text)

        # at this point, remaining words are non-cleaned words
        if self._misspelled_words:
            check_text = self.new_text(check_text)

            # check the against the general words again, now with word
            # cleaning
            self._misspelled_words = (
                    unknown(check_text, "general", self._cursor,
                            file_exts=True))
            if self._misspelled_words:
                check_text = self.new_text(check_text)
                self._misspelled_words = (
                        unknown(check_text, "non_english", self._cursor,
                                file_exts=True))

            if self._misspelled_words:
                check_text = self.new_text(check_text)
                for lstname in exact_matches:
                    if self._misspelled_words:
                        self._misspelled_words = (
                                unknown(check_text, lstname, self._cursor))
                        if self._misspelled_words:
                            check_text = self.new_text(check_text)

        if self._misspelled_words:
            check_text = self.new_text(check_text)
            if text.find("-") >= 0:
                # check compound (hyphen) words in the text case-insensitive
                # against the general words
                self._misspelled_words = (
                        unknown(check_text, "general", self._cursor,
                                separator="-"))

        if self._misspelled_words:
            check_text = self.new_text(check_text)
            if text.find("\u2013") >= 0:
                # check compound (unicode En-dash) words in the text
                # case-insensitive against the general words
                self._misspelled_words = (
                        unknown(check_text, "general", self._cursor,
                                separator="\u2013"))

        if self._misspelled_words:
            check_text = self.new_text(check_text)
            if text.find("/") >= 0:
                # check compound (slash) words in the text case-insensitive
                # against the general words
                self._misspelled_words = (
                        unknown(check_text, "general", self._cursor,
                                separator="/"))

        if self._misspelled_words:
            check_text = self.new_text(check_text)
            separator = ""
            if text.find("/") > 0:
                separator = "/"

            if len(separator) == 0:
                if text.find("-") > 0:
                    separator = "-"

            if len(separator) > 0:
                # check compound words in the text directly against the
                # acronyms
                self._misspelled_words = (
                        unknown(check_text, "acronyms", self._cursor,
                                separator=separator))

        if self._misspelled_words:
            check_text = text
            check_text = check_text.replace("\n", " ").strip()
            check_text = self.new_text(check_text, includePrevious=True)
            # check text directly against the unit abbreviations valids
            self._misspelled_words = (unknown(check_text, "unit_abbrevs",
                                              self._cursor))

        if self._misspelled_words:
            check_text = self.new_text(check_text)
            if text.find("_") >= 0:
                # check snake_case words in the text case-insensitive against
                # the general words
                self._misspelled_words = (
                        unknown(check_text, "general", self._cursor,
                                separator="_"))

        # ignore 'unknown' acronyms
        if self._misspelled_words:
            for x in range(0, len(self._misspelled_words)):
                word = strip_plural(self._misspelled_words[x].replace(".", ""))
                if word.isalnum() and word == word.upper():
                    self._misspelled_words[x] = ""
                else:
                    parts = word.split("/")
                    if len(parts) > 1:
                        for y in range(0, len(parts)):
                            if (parts[y].isalnum() and parts[y] ==
                                    parts[y].upper()):
                                parts[y] = ""

                        check_text = " ".join([e for e in parts if len(e) > 0])
                        if len(check_text) == 0:
                            self._misspelled_words[x] = ""
                        else:
                            self._misspelled_words[x] = (
                                    unknown(check_text, "exact_others",
                                            self._cursor))

            #self._misspelled_words = [e for e in self._misspelled_words if
            #                          len(e) > 0]
            l = self._misspelled_words
            self._misspelled_words = []
            for e in l:
                if isinstance(e, list):
                    for x in e:
                        self._misspelled_words.append(x)
                else:
                    self._misspelled_words.append(e)

    def new_text(self, text, **kwargs):
        """
        Builds the text to check from the list of misspelled words.
        """
        if 'includePrevious' in kwargs and kwargs['includePrevious']:
            words = text.split()
            text = ""
            if words[0] == self._misspelled_words[0]:
                text = "XX " + self._misspelled_words[0]
                midx = 1
            else:
                midx = 0

            for n in range(1, len(words)):
                if midx == len(self._misspelled_words):
                    break

                stripped, pword = strip_punctuation(words[n])
                while stripped:
                    stripped, pword = strip_punctuation(pword)

                if self._misspelled_words[midx] in (
                        words[n], clean_word(words[n]), pword,
                        words[n].strip()):
                    text += (" " + words[n-1] + " " +
                             self._misspelled_words[midx])
                    midx += 1

            return text

        return " ".join(self._misspelled_words)
