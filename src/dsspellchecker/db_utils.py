import getopt
import inspect
import os
import shutil
import sqlite3
import sys


db_config = {
    'general': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': True,
    },
    'unit_abbrevs': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'places': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'names': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'exact_others': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'non_english': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': True,
    },
    'file_exts': {
        'columns': ["word"],
        'primary_key': "word",
        'icase': False,
    },
    'acronyms': {
        'columns': ["word", "description"],
        'primary_key': "word",
        'icase': False,
    },
}


def build_db(args):
    if args[0] == "-h":
        func_name = inspect.currentframe().f_code.co_name
        print((
            "usage: {} {}".format(args[-1], func_name) + "\n"
            "\n"
            "This command builds the spellchecker database from the word lists. It doesn't\n"
            "take any arguments. Use this command after installing the spellchecker to\n"
            "initialize the database.\n"
        ))
        sys.exit(1)

    print("Building database from lists of valids ...")
    dict_dir = os.path.join(os.path.dirname(__file__), "dictionary")
    db_name = os.path.join(dict_dir, "valids.db")
    if os.path.exists(db_name):
        os.unlink(db_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for e in db_config:
        cursor.execute("create table if not exists " + e + " (" + ", ".join("{} text nocollate nocase".format(t) for t in db_config[e]['columns']) + ", primary key (" + db_config[e]['primary_key'] + "))")
        with open(os.path.join(dict_dir, e + ".lst")) as f:
            lines = f.readlines()

        for line in lines:
            words = line.split("|")
            cursor.execute("insert into " + e + " (" + ", ".join(db_config[e]['columns']) + ") values (" + ", ".join("?" for word in words) + ") on conflict do nothing", tuple(word.strip() for word in words))
            conn.commit()

    conn.close()
    print("... done.")


def add_words(args):
    util_name = args[-1]
    del args[-1]
    try:
        if len(args) == 0:
            raise getopt.GetoptError("missing input")

        if args[0] == "-h":
            raise getopt.GetoptError("")

        opts, args = getopt.getopt(args, "t:w:")
    except getopt.GetoptError as err:
        func_name = inspect.currentframe().f_code.co_name
        if len(str(err)) > 0:
            print("Error: {}\n".format(err))

        print((
            "usage: {} {} -t <table> -w <words> ...".format(util_name, func_name) + "\n"
            "\n"
            "required:\n"
            "    -t <table>   name of table where word(s) will be inserted\n"
            "    -w <words>   words to insert\n"
            "                   can be a string - e.g. -w \"word1 word2 word3\"\n"
            "                   can be repeated - e.g. -w word1 -w word2\n"
        ))
        sys.exit(1)

    words = []
    for opt, arg in opts:
        if opt == "-t":
            table = arg
        elif opt == "-w":
            l = arg.split()
            words.extend(l)

    if 'table' not in locals():
        raise UnboundLocalError("no table was specified")

    if table not in db_config:
        raise NameError("table '" + table + "' does not exist")

    if len(words) == 0:
        raise RuntimeError("no words were specified")

    try:
        dict_dir = os.path.join(os.path.dirname(__file__), "dictionary")
        conn = sqlite3.connect(os.path.join(dict_dir, "valids.db"))
        cursor = conn.cursor()
        for x in range(0, len(words)):
            if db_config[table]['icase']:
                words[x] = words[x].lower()

            cursor.execute("insert into " + table + " values (?)", (words[x], ))

        conn.commit()
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        raise RuntimeError(e)

    conn.close()


def add_acronym(args):
    util_name = args[-1]
    del args[-1]
    try:
        if len(args) == 0:
            raise getopt.GetoptError("missing input")

        if args[0] == "-h":
            raise getopt.GetoptError("")

        opts, args = getopt.getopt(args, "a:d:")
    except getopt.GetoptError as err:
        func_name = inspect.currentframe().f_code.co_name
        if len(str(err)) > 0:
            print("Error: {}\n".format(err))

        print((
            "usage: {} {} -a <acronym> -d <description>".format(util_name, func_name) + "\n"
            "\n"
            "required:\n"
            "    -a <acronym>     the acronym to add\n"
            "    -f <full_name>   the full name of the acronym\n"
        ))
        sys.exit(1)

    for opt, arg in opts:
        if opt == "-a":
            acronym = arg
        elif opt == "-f":
            full_name = arg

    if 'acronym' not in locals():
        raise UnboundLocalError("no acronym was specified")

    if 'full_name' not in locals():
        raise UnboundLocalError("full name for the acronym not specified")

    try:
        dict_dir = os.path.join(os.path.dirname(__file__), "dictionary")
        conn = sqlite3.connect(os.path.join(dict_dir, "valids.db"))
        cursor = conn.cursor()
        cursor.execute("insert into acronyms values (?, ?)", (acronym.upper(), full_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        raise RuntimeError(e)

    conn.close()


def dump_db(args, **kwargs):
    util_name = args[-1]
    del args[-1]
    try:
        if len(args) > 0:
            if args[0] == "-h":
                raise getopt.GetoptError("")

            opts, args = getopt.getopt(args, "", ["dir="])
    except getopt.GetoptError as err:
        func_name = inspect.currentframe().f_code.co_name
        if len(str(err)) > 0:
            print("Error: {}\n".format(err))

        print((
            "usage: {} {} [--dir=<path>]".format(util_name, func_name) + "\n"
            "\n"
            "This command dumps the current spellchecker database into the component word\n"
            "lists in the distribution directory, so that if the database is rebuilt, it\n"
            " will use the most up-to-date lists. Include an optional path to create the\n"
            " lists elsewhere so that if you have to reinstall the package, you can build\n"
            " the database from custom word lists instead of distribution word lists.\n"
            "\n"
            "options:\n"
            "--dir=<path>   additional path for the dumped word lists\n"
        ))
        sys.exit(1)

    verbose = False if 'quiet' in kwargs and kwargs['quiet'] else True
    dict_dir = os.path.join(os.path.dirname(__file__), "dictionary")
    if 'opts' in locals() and opts[0][0] == "--dir":
        custom_dir = opts[0][1]
        if not os.path.exists(custom_dir):
            raise FileNotFoundError("the specified directory does not exist")

    db_name = os.path.join(dict_dir, "valids.db")
    conn = sqlite3.connect(os.path.join(dict_dir, "valids.db"))
    cursor = conn.cursor()
    for e in db_config:
        cursor.execute("select " + ", ".join(db_config[e]['columns']) + " from " + e)
        res = cursor.fetchall()
        if len(res) == 0:
            raise sqlite3.Error("table '{}' is empty".format(e))

        fname = e + ".lst"
        if verbose:
            print("Writing  {} entries to '{}' ...".format(str(len(res)), fname))

        with open(os.path.join(dict_dir, fname), "w") as f:
            for l in res:
                f.write(" | ".join(x for x in l) + "\n")

        if 'custom_dir' in locals():
            with open(os.path.join(custom_dir, fname), "w") as f:
                for l in res:
                    f.write(" | ".join(x for x in l) + "\n")

    conn.close()
    if verbose:
        print("... done.")


def dsspellchecker_manage():
    util_name = inspect.currentframe().f_code.co_name
    args = sys.argv[1:] + [util_name]
    if len(args) < 2:
        print((
            "usage: {} <command> [args...]".format(util_name) + "\n"
            "\n"
            "command:\n"
            "    add_words     add words to the spellchecker database\n"
            "    add_acronym   add an acronym to the spellchecker database\n"
            "    build_db      build the spellchecker database\n"
            "    dump_db       dump the spellchecker database\n"
            "\n"
            "use `{} <command> -h` to get help for the specific command".format(util_name) + "\n"
        ))
        sys.exit(1)

    if args[0] == "build_db":
        build_db(args[1:])
    elif args[0] == "add_words":
        add_words(args[1:])
    elif args[0] == "add_acronym":
        add_acronym(args[1:])
    elif args[0] == "dump_db":
        dump_db(args[1:])
    else:
        raise ValueError("invalid command")


if __name__ == "__main__":
    dsspellchecker_manage()
