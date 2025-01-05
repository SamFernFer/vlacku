import sys, os, re
import xml.etree.ElementTree as ET
from typing import Pattern

# Prints the help message.
def getHelp(what: str):
    if 
    # Retrieves the escape character for the current system.
    _esc: str = '^' if os.name == "nt" else '\\'
    # The characters which need escaping.
    _chars = [ '&', '|', '!' ]

    # Escape the characters which need escaping in the argument.
    def escapeArg(arg: str):
        return "".join(_esc + c if c in _chars else c for c in arg)
    
    _examples: list = [
        (
            [ "user/username=officialdata", "&", "type=gismu" ],
            "Lists all official gismu (and experimental gismu, if any are official)"
        ),
        (
            [ "glossword/word=^or$" ],
            "Lists all words with one glossword which is exacly \"or\""
        ),
        # (
        #     [ ],
        #     'Lists all two-letter cmavo which end in "e" and do not begin with "d"'
        # )
    ]
    # Retrieves the file's name.
    _name: str = os.path.basename(__file__)

    print(f"Usage: {str} (--paths | expr)\n")
    print(
        'expr is a boolean expression whose conditions are of the form "<path>=<pattern>". '
        '<path> is a path to an XML node or attribute inside each valsi node, with "/" as the '
        "separator. <pattern> is a regex pattern which must be present inside the node's text "
        "or the attribute's value. Parentheses are supported. Conditions without operators in "
        'between are treated as if they were joined by "&". The operators and their '
        "precedences (a lower precedence means getting evaluated first) are the following "
        "(note that on most shells they should be escaped):\n"
        '- ! (unary): 1\n'
        '- & (binary): 2\n'
        '- | (binary): 3\n'
    )
    exit(0)
if len(sys.argv) < 2:
    getHelp(None)

_dbPath: str = "vlaste/jbovlaste-en.xml"

_expectedOptions = [
    (    "help", "h",  [0, 1],
        'Displays help information. Pass "operators" to view the list of operators '
        'and "paths" to view the list of possible paths.'
    ),
    ( "version", "V",  0, "Displays the program's version." )
]

_expectedLongOptions: dict = {}
_expectedShortOptions: dict = {}

# Builds the dicts for the expected options.
for e in _expectedOptions:
    if e[0] is not None: _expectedLongOptions[e[0]] = e
    if e[1] is not None: _expectedShortOptions[e[1]] = e

_tokens: list = []
_longOptions: list = []
_shortOptions: list = []

for i in range(1, len(sys.argv)):
    _arg: str = sys.argv[i]
    if _arg.startswith('--'):
        if _expectedLongOptions.get(_arg[2:]) is not None:
            _longOptions.append(
        else:
            f
    elif _arg.startswith('-'):
    else:
        _tokens.append(_arg)

if "help" in _longOptions or "h" in _shortOptions:
    getHelp()

exit(0)

def runMatch(elem: ET.Element, path: str, pattern: Pattern[str])->bool:
    _pos: int = path.find('/')
    # If the path has any subpath, then one of the indirect children must match.
    if _pos > 0:
        _head: str = path[:_pos]
        _tail: str = path[_pos + 1:]
        # Returns true if at least one of the indirect childrens' texts match the pattern.
        for v in elem.findall(_head):
            if match(v, _tail, pattern):
                return True
    # Else, one of the direct children must match.
    else:
        # Attributes cannot have children, so they are only considered when 
        # the path contains no path separators ('/').
        for v in elem.findall(path):
            if pattern.search(v.text) is not None:
                return True
        if a := elem.attrib.get(path):
            if pattern.search(a) is not None:
                return True
    return False

with open(_dbPath, "rb") as _dbFile:
    _tree = ET.ElementTree(ET.fromstring(_dbFile.read().decode("utf-8")))
    _root = _tree.getroot()
    _list = None

    # Searches for the right direction.
    for e in _root:
        # If the tag contains the "from" and "to" attributes.
        if (_from := e.attrib.get("from")) and (_to := e.attrib.get("to")):
            # Finds the lojban to English direction.
            if _from == "lojban" and _to == "English":
                _list = e
                break
    if _list is None:
        print("ERROR: Could not find the lojban to English direction.")
        exit(-1)

    for v in _list:
        if runMatch(v, _path, _regex):
            print(ET.tostring(v, encoding='utf-8').decode('utf-8'))

def match(index: int, tokens: list)->tuple[str, Pattern[str]]:
    _pair: str = tokens[index]
    _index: int = _pair.find('=')

    _path = _pair[:_index]
    _pattern = _pair[_index + 1:]

    if len(_path) <= 0:
        raise Exception("ERROR: empty path.")
    if len(_pattern) <= 0:
        raise Exception("ERROR: empty pattern.")
    return (_path, re.compile(_pattern))

def expr0():


# and ::= "&"
# or  ::= "|"
# not ::= "!"
# match ::= name"="name

# expr0 ::= match | "(" exprN ")"
# expr1 ::= expr0 | not expr0
# expr2 ::= expr1 | expr1 | expr1 and expr1
# expr3 ::= expr2 | expr2 or expr2
# exprN ::= expr3

