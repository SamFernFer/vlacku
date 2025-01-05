import sys, os, re, json
import xml.etree.ElementTree as ET
from typing import Pattern

_dbPath: str = "vlaste/jbovlaste-en.xml"

# Prints the help message.
def getHelp(what: str):
    def generalHelp():
        # Retrieves the escape character for the current system.
        _esc: str = '^' if os.name == "nt" else '\\'
        # The characters which need escaping.
        _chars = [ '&', '|', '!' ]

        # Escape the characters which need escaping in the argument.
        def escapeArg(arg: str):
            return "".join((_esc + c if c in _chars else c) for c in arg)
        
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
    def operators():
        print("Operators (and their types and precedences):\n")
        print("! (unary) = not (1)")
        print("& (binary) = and (2)")
        print("| (binary) = or (3)")
        print()
        print("Notes:\n")
        print("- Grouping is done with parentheses;")
        print("- On most systems, you must escape the operators and parentheses;")
    _helpMap = {
        "operators": operators,
        "ops": operators
    }
    _func: function = _helpMap.get(what)
    if _func is None:
        generalHelp()
    else:
        _func()
def getVersion():
    print("Version 1.0")

if len(sys.argv) < 2:
    getHelp(None)

_expectedOptions = [
    (   "help", "h",  [0, 1],
        'Displays help information. Pass "operators" or "ops" to view the list of operators '
        'and "paths" to view the list of possible paths.'
    ),
    ( "version", "V",  [0], "Displays the program's version." )
]

_expectedLongOptions: dict = {}
_expectedShortOptions: dict = {}

# Builds the dicts for the expected options.
for e in _expectedOptions:
    if e[0] is not None: _expectedLongOptions[e[0]] = e
    if e[1] is not None: _expectedShortOptions[e[1]] = e

_tokens: list = []

_longOptions: dict = {}
_shortOptions: dict = {}

# Returns a list with the maximum possible number of elements specified in amounts.
# Throws if no amount is possible.
def getOptArgs(opt: str, index: int, amounts: list):
    # Sorts the list of expected amounts.
    amounts.sort(reverse=True)
    # If no arguments are expected because the list is empty or the largest possibility 
    # is smaller or equal to zero.
    if len(amounts) == 0 or amounts[0] <= 0: return []

    # 3 - 2 = 1

    _amount: int = -1
    for a in amounts:
        if len(sys.argv) - index > a:
            # Sets the _amount to the largest possible number of required arguments.
            _amount = a
            break

    # If there are not enough arguments.
    if _amount < 0:
        raise Exception(
            f"Option {json.dumps(opt)} expected at least {amounts[0]} argument{'s' if amounts[0] != 1 else ''}."
        )
    
    # If there are enough arguments.
    return sys.argv[index + 1:index + 1 + _amount]

i: int = 1
while i < len(sys.argv):
    _arg: str = sys.argv[i]
    # Parses the long options.
    if _arg.startswith('--'):
        _optName: str = _arg[2:]
        _opt = _expectedLongOptions.get(_optName)
        if _opt is not None:
            _args: list = getOptArgs(_optName, i, _opt[2])
            _longOptions[_optName] = _args
            i += len(_args)
        else:
            raise Exception(f"Unrecognised long option {json.dumps(_optName)}")
    # Parses the short options.
    elif len(_arg) > 1 and _arg.startswith('-'):
        _optName = _arg[1:]
        _opt = _expectedShortOptions.get(_optName)
        if _opt is not None:
            _args: list = getOptArgs(_optName, i, _opt[2])
            _shortOptions[_optName] = _args
            i += len(_args)
        else:
            raise Exception(f"Unrecognised short option {json.dumps(_optName)}")
    else:
        _tokens.append(_arg)
    # Increments the index.
    i += 1


_helpOpt = _longOptions.get("help") or _shortOptions.get("h")
if _helpOpt is not None:
    _section = _helpOpt[0] if (len(_helpOpt) > 0) else None
    getHelp(_section)

_verOpt = _longOptions.get("version") or _shortOptions.get("V")
if _verOpt is not None:
    getVersion()

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
    pass

# and ::= "&"
# or  ::= "|"
# not ::= "!"
# match ::= name"="name

# expr0 ::= match | "(" exprN ")"
# expr1 ::= expr0 | not expr0
# expr2 ::= expr1 | expr1 | expr1 and expr1
# expr3 ::= expr2 | expr2 or expr2
# exprN ::= expr3

