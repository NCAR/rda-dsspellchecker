# dsspellchecker

This spellchecker validates the words in a text string and returns a list of words that fail to validate.

The project was developed mainly for the purpose of validating the text fields of the dataset metadata for the NSF NCAR Research Data Archive. This means that the dictionary is mainly geoscience- and dataset-focused, and you might not find words, like 'beautiful' for example, that you otherwise expect to find. There is a way to add words to the dictionary, but be aware that if you want to use it for more general use, it will likely require numerous additions.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dsspellchecker.

From within your python environment:
1. run `pip install git+https://github.com/NCAR/rda-dsspellchecker`
2. build the spellchecker database from the command line: `dsspellchecker_manage build_db`

## Usage

```python
from dsspellchecker import SpellChecker

spell_checker = SpellChecker()
print(spell_checker.ready)
# True if the spellchecker is ready, False if error

print(spell_checker.error)
# '' for no error (ready == True), otherwise some message

# check some text
spell_checker.check("This dataset contains data from a reanalysis model. Parameters include "
    "temperature at 2 meters and winds at 10 meters.")
print(spell_checker.misspelled_words)
# prints [] because all words validate

# check some text with two misspellings
spell_checker.check("This datset contains data from a reanalysis model. Parmeters include "
    "temperature at 2 meters and winds at 10 meters.")
print(spell_checker.misspelled_words)
# prints ['datset', 'Parmeters'] for the two misspelled words
```

## Dictionary

The dictionary is divided up into several word lists. Some of this is functional (affects the way the spellchecker does validation) and some of this is simply organizational (grouping of like words). The various lists and their functions follow:

**general.lst:** list of "everyday" words; the spellchecker will validate words case-insensitively against these entries (e.g. 'world', 'World', and 'wORld' will all validate as being spelled correctly)

**acronyms.lst:** list of acronyms and their full descriptions; the spellchecker will validate words exactly against the acronyms and the words in the full descriptions (e.g. 'NCAR' will validate, but 'nCAR' will not; from NCAR's description, the words 'National', 'Center', 'for', 'Atmospheric', 'Research' will also validate)

**names.lst:** list of people and other names (except geographic - see **places.lst**); the spellchecker will validate words exactly against these entries

**places.lst:** list of geographic place names; the spellchecker will validate words exactly against these entries

**exact_others.lst:** list of other exact matches that don't fit into acronyms, names, or places; the spellchecker will validate words exactly against these entries

**unit_abbrevs.lst:** list of unit abbreviations that will validate IF they are preceeded by a number; e.g. "500 mbar" will validate, but "mbar" by itself will not

**file_exts.lst:** list of known file extensions, so that filenames will validate; e.g. "global_tmp.nc" will validate, but "global_tmp.nc7" will not

**non_english.lst:** list of non-English words; the spellchecker will validate words exactly against these entries

## Scripts

**dsspellchecker_manage**

Run `dsspellchecker_manage` with no arguments to get usage information

- sub-commands: run `dsspellchecker_manage <sub-command> -h` for help on the given sub-command

    - `add_words`: add words to the spellchecker database
    - `add_acronym`: add an acronym to the spellchecker database
    - `build_db`: build the spellchecker database from the word lists
    - `dump_db`: dump the current spellchecker database to the component word lists
