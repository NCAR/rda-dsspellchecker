import re
import string

from libpkg.strutils import strip_plural, strip_punctuation

from .db_utils import is_valid_word


def unknown(text, lstname, cursor, **kwargs):
    misspelled_words = []
    words = text.split()
    checking_units = True if lstname == "unit_abbrevs" else False
    separator = kwargs['separator'] if 'separator' in kwargs else ""
    ikwargs = {}
    if 'file_exts' in kwargs and kwargs['file_exts']:
        ikwargs.update({'file_exts': True, 'cursor': cursor})

    do_clean = kwargs['cleanWord'] if 'cleanWord' in kwargs else True
    n = 0 if not checking_units else 1
    while n < len(words):
        if do_clean:
            words[n] = clean_word(words[n])
        else:
            words[n] = trim_front(words[n])

        if words[n] in misspelled_words:
            n += 1
            continue

        cword = words[n]
        if 'trimPlural' in kwargs and kwargs['trimPlural']:
            cword = strip_plural(cword)

        if ignore_word(cword, **ikwargs):
            n += 1
            continue

        if cword[0:4] == "non-":
            cword = cword[4:]

        if len(separator) == 0:
            if checking_units:
                if is_valid_word(cword, lstname, cursor):
                    pword = words[n-1].strip() if n > 0 else "XX"
                    pword = clean_word(pword)
                    if pword == "et" and cword == "al":
                        pass
                    elif not pword.replace(".", "").isnumeric():
                        misspelled_words.append(words[n])

                else:
                    if n > 0:
                        if (len(cword) == 1 and cword.isalpha() and cword ==
                                cword.upper() and words[n-1].lower() ==
                                "station"):
                            # allow for e.g. 'Station P'
                            pass

                        else:
                            misspelled_words.append(words[n])

                    else:
                        misspelled_words.append(words[n])

                n += 1
            else:
                if cword[-2:] == "'s":
                    cword = cword[:-2]

                if not is_valid_word(cword, lstname, cursor):
                    misspelled_words.append(words[n])

        else:
            parts = cword.split(separator)
            m = 0
            failed = False
            while m < len(parts):
                if (not ignore_word(parts[m], **ikwargs) and not
                        is_valid_word(parts[m], lstname, cursor)):
                    if parts[m][-2:] == "'s":
                        if not is_valid_word(parts[m][:-2], lstname, cursor):
                            failed = True
                            break

                    else:
                        failed = True

                m += 1

            if failed:
                misspelled_words.append(words[n])

        n += 1

    return misspelled_words


def ignore_word(word, **kwargs):
    if len(word) == 0:
        return True

    # ignore numbers
    if len(word) > 1 and word[0] == '#' and word[1:].isnumeric():
        return True

    # ignore integers, floats and currency values
    if word[0] in ('-', '$'):
        word = word[1:]

    if len(word) > 3 and word[0:2] == "($" and word[-1] == ')':
        word = word[2:-1]

    if word.replace(".", "").replace(",", "").isnumeric():
        return True

    # ignore acronyms containing all capital letters and numbers
    #if word.isalpha() and word == word.upper():
    #    return True

    # ignore ratios (e.g. 9:3), fractions, and dates (e.g. 10/1/2005)
    if word.replace(":", "").replace("/", "", 2).isnumeric():
        return True

    # ignore e.g. 1900s
    if len(word) > 0 and word[-1] == "s" and word[:-1].isnumeric():
        return True

    # ignore ordinal numbers
    if (len(word) > 2 and word[-2:] == "st" and word[:-2].isnumeric() and
            word[-3] == '1'):
        return True

    if (len(word) > 2 and word[-2:] == "nd" and word[:-2].isnumeric() and
            word[-3] == '2'):
        return True

    if (len(word) > 2 and word[-2:] == "rd" and word[:-2].isnumeric() and
            word[-3] == '3'):
        return True

    if (len(word) > 2 and word[-2:] == "th" and word[:-2].isnumeric() and
            word[-3] in ('0', '4', '5', '6', '7', '8', '9')):
        return True

    # ignore NG-GDEX dataset IDs
    if len(word) == 7 and word[0] == 'd' and word[1:].isnumeric():
        return True

    # ignore legacy dataset IDs
    if (len(word) == 7 and word[0:2] == "ds" and word[5] == '.' and
            word[2:].replace(".", "").isnumeric()):
        return True

    # ignore e.g. pre-1950
    if len(word) > 4 and word[0:4] == "pre-" and word[4:].isnumeric():
        return True

    # ignore version numbers e.g. v2.0, 0.x, 1a
    if (len(word) > 1 and word[0] == 'v' and
            word[1:].replace(".", "").isnumeric()):
        return True

    if len(word) > 2 and word[-2:] == ".x" and word[:-2].isnumeric():
        return True

    rexp = re.compile("^[0-9]{1,}[a-zA-Z]{1,}$")
    if rexp.match(word):
        return True

    # ignore NCAR Technical notes
    rexp = re.compile(r"^NCAR/TN-([0-9]){1,}\+STR$")
    if rexp.match(word):
        return True

    # ignore itemizations
    rexp = re.compile(r"^[a-zA-Z][\.)]$")
    if rexp.match(word):
        return True

    # ignore references
    rexp = re.compile(r"^\([a-zA-Z0-9]{1,3}\)$")
    if rexp.match(word):
        return True

    rexp = re.compile(r"^\([ivx]{1,7}\)$")
    if rexp.match(word):
        return True

    # ignore email addresses
    rexp = re.compile(r"^(.){1,}@((.){1,}\.){1,}(.){2,}$")
    if rexp.match(word):
        return True

    # ignore file extensions
    rexp = re.compile(r"^\.([a-zA-Z0-9]){1,10}$")
    if rexp.match(word):
        return True

    # ignore file names
    idx = word.rfind(".")
    if (idx > 0 and 'file_exts' in kwargs and kwargs['file_exts'] and
            is_valid_word(word[idx+1:], "file_exts", kwargs['cursor'])):
        return True

    # ignore acronyms like TS1.3B.4C
    #rexp = re.compile("^[A-Z0-9]{1,}(\.[A-Z0-9]{1,}){0,}$")
    #if rexp.match(word):
    #    return True

    # ignore URLs
    rexp = re.compile(r"^\[{0,1}https{0,1}://")
    if rexp.match(word):
        return True

    rexp = re.compile(r"^\[{0,1}ftp://")
    if rexp.match(word):
        return True

    rexp = re.compile(r"^\[{0,1}mailto:")
    if rexp.match(word):
        return True

    # ignore DOIs
    rexp = re.compile(r"^10\.\d{4,}/.{1,}$")
    if rexp.match(word):
        return True

    # ignore references to ARKs
    rexp = re.compile(r"^\(ark:/(\d{5}|\d{9})/(.){2,}\)$")
    if rexp.match(word):
        return True

    return False


def clean_word(word):
    if len(word) == 0:
        return ""

    # strip html entities
    entity = re.compile(r"&\S{1,};")
    m = entity.findall(word)
    for e in m:
        word = word.replace(e, "")

    if len(word) == 0:
        return ""

    stripped, word = strip_punctuation(word)
    while stripped:
        if len(word) == 0:
            return ""

        stripped, word = strip_punctuation(word)

    cleaned_word = False
    if word[0] in ('"', '\''):
        word = word[1:]
        cleaned_word = True

    if word[0] == '(' and (word[-1] == ')' or word.find(")") < 0):
        word = word[1:]
        cleaned_word = True

    if word[-1] in (',', '"', '\''):
        word = word[:-1]
        if len(word) == 0:
            return

        cleaned_word = True

    rexp = re.compile(r"\(s\)$")
    if word[-1] == ")" and not rexp.search(word):
        word = word[:-1]
        if len(word) == 0:
            return

        cleaned_word = True

    if len(word) >= 2 and word[-2:] == ").":
        word = word[:-2]
        if len(word) == 0:
            return

        cleaned_word = True

    if (len(word) >= 2 and word[-2] == "-" and word[-1] in
            string.ascii_uppercase):
        word = word[:-2]
        if len(word) == 0:
            return

        cleaned_word = True

    if cleaned_word:
        word = clean_word(word)

    return word


def trim_front(word):
    while len(word) > 0 and word[0] in ('(', '[', '{', '"', '\'', '`'):
        word = word[1:]

    return word
