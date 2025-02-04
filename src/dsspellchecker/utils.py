import re
import string

from libpkg.strutils import strip_plural, strip_punctuation


def unknown(text, valids, **kwargs):
    misspelled_words = []
    words = text.split()
    icase = kwargs['icase'] if 'icase' in kwargs else False
    checking_units = kwargs['units'] if 'units' in kwargs else False
    separator = kwargs['separator'] if 'separator' in kwargs else ""
    file_ext_valids = kwargs['file_ext_valids'] if 'file_ext_valids' in kwargs else None
    do_clean = kwargs['cleanWord'] if 'cleanWord' in kwargs else True
    n = 0 if not checking_units else 1
    while n < len(words):
        if do_clean:
            words[n] = clean_word(words[n])

        if words[n] not in misspelled_words:
            cword = words[n]
            if 'trimPlural' in kwargs and kwargs['trimPlural']:
                cword = strip_plural(cword)

            if validate_word(cword, file_ext_valids):
                if cword[0:4] == "non-":
                    cword = cword[4:]

                if icase:
                    cword = cword.lower()

                if len(separator) == 0:
                    if checking_units:
                        if cword in valids:
                            pword = words[n-1].strip() if n > 0 else "XX"
                            if pword == "et" and cword == "al":
                                pass
                            elif not pword.replace(".", "").isnumeric():
                                misspelled_words.append(words[n])

                        else:
                            if n > 0:
                                if len(cword) == 1 and cword.isalpha() and cword == cword.upper() and words[n-1].lower() == "station":
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

                        if cword not in valids:
                            misspelled_words.append(words[n])

                else:
                    parts = cword.split(separator)
                    m = 0
                    failed = False
                    while m < len(parts):
                        if validate_word(parts[m], file_ext_valids) and parts[m] not in valids:
                            if parts[m][-2:] == "'s":
                                if parts[m][:-2] not in valids:
                                    failed = True
                                    break

                            else:
                                failed = True

                        m += 1

                    if failed:
                        misspelled_words.append(words[n])

        n += 1

    return misspelled_words


def validate_word(word, file_ext_valids):
    if len(word) == 0:
        return False

    # ignore numbers
    if len(word) >= 2 and word[0] == '#' and word[1:].isnumeric():
        return False

    # ignore integers, floats and currency values
    if word[0] in ('-', '$'):
        word = word[1:]

    if len(word) > 3 and word[0:2] == "($" and word[-1] == ')':
        word = word[2:-1]

    if word.replace(".", "").replace(",", "").isnumeric():
        return False

    # ignore acronyms containing all capital letters and numbers
    #if word.isalpha() and word == word.upper():
    #    return False

    # ignore ratios (e.g. 9:3), fractions, and dates (e.g. 10/1/2005)
    if word.replace(":", "").replace("/", "", 2).isnumeric():
        return False

    # ignore e.g. 1900s
    if word[-1] == "s" and word[:-1].isnumeric():
        return False

    # ignore ordinal numbers
    if word[-2:] == "st" and word[:-2].isnumeric() and word[-3] == '1':
        return False

    if word[-2:] == "nd" and word[:-2].isnumeric() and word[-3] == '2':
        return False

    if word[-2:] == "rd" and word[:-2].isnumeric() and word[-3] == '3':
        return False

    if word[-2:] == "th" and word[:-2].isnumeric() and word[-3] in ('0', '4', '5', '6', '7', '8', '9'):
        return False

    # ignore NG-GDEX dataset IDs
    if len(word) == 7 and word[0] == 'd' and word[1:].isnumeric():
        return False

    # ignore e.g. pre-1950
    if word[0:4] == "pre-" and word[4:].isnumeric():
        return False

    # ignore version numbers e.g. v2.0, 0.x, 1a
    if word[0] == 'v' and word[1:].replace(".", "").isnumeric():
        return False

    if word[-2:] == ".x" and word[:-2].isnumeric():
        return False

    rexp = re.compile("^[0-9]{1,}[a-zA-Z]{1,}$")
    if rexp.match(word):
        return False

    # ignore NCAR Technical notes
    rexp = re.compile("^NCAR/TN-([0-9]){1,}\+STR$")
    if rexp.match(word):
        return False

    # ignore itemizations
    rexp = re.compile("^[a-zA-Z][\.)]$")
    if rexp.match(word):
        return False

    # ignore references
    rexp = re.compile("^\([a-zA-Z0-9]{1,3}\)$")
    if rexp.match(word):
        return False

    rexp = re.compile("^\([ivx]{1,7}\)$")
    if rexp.match(word):
        return False

    # ignore email addresses
    rexp = re.compile("^(.){1,}@((.){1,}\.){1,}(.){2,}$")
    if rexp.match(word):
        return False

    # ignore file extensions
    rexp = re.compile("^\.([a-zA-Z0-9]){1,10}$")
    if rexp.match(word):
        return False

    # ignore file names
    idx = word.rfind(".")
    if idx > 0 and file_ext_valids != None and word[idx+1:] in file_ext_valids:
        return False

    # ignore acronyms like TS1.3B.4C
    #rexp = re.compile("^[A-Z0-9]{1,}(\.[A-Z0-9]{1,}){0,}$")
    #if rexp.match(word):
    #    return False

    # ignore URLs
    rexp = re.compile("^\[{0,1}https{0,1}://")
    if rexp.match(word):
        return False

    rexp = re.compile("^\[{0,1}ftp://")
    if rexp.match(word):
        return False

    rexp = re.compile("^\[{0,1}mailto:")
    if rexp.match(word):
        return False

    # ignore DOIs
    rexp = re.compile("^10\.\d{4,}/.{1,}$")
    if rexp.match(word):
        return False

    return True


def clean_word(word):
    if len(word) == 0:
        return ""

    # strip html entities
    entity = re.compile("&\S{1,};")
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

    rexp = re.compile("\(s\)$")
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

    if len(word) >= 2 and word[-2] == "-" and word[-1] in string.ascii_uppercase:
        word = word[:-2]
        if len(word) == 0:
            return

        cleaned_word = True

    if cleaned_word:
        word = clean_word(word)

    return word
