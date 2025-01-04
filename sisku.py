import sys, os, re
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Pattern

if len(sys.argv) != 2:
    print(f"Usage: {os.path.basename(__file__)} <path>=<pattern>")
    print()
    print(
        "<path> is a tag or attribute path (separated by '/' and without './' at the start) "
        "inside each valsi. <pattern> is the Regex pattern which the tag's text must at least "
        "partially match."
    )
    print("Example: sisku.py user/username=officialdata")
    exit(0)

_dbPath: str = "jbovlaste-en.xml"

_pair: str = sys.argv[1]
_index: int = _pair.find('=')

_path = _pair[:_index]
_pattern = _pair[_index + 1:]

_shouldExit: bool = False
if len(_path) <= 0:
    print("ERROR: empty path.")
    _shouldExit = True
if len(_pattern) <= 0:
    print("ERROR: empty pattern.")
    _shouldExit = True

if _shouldExit: exit(-1)

_regex: Pattern[str] = re.compile(_pattern)

def match(elem: ET.Element, path: str, pattern: Pattern[str])->bool:
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
        if match(v, _path, _regex):
            print(ET.tostring(v, encoding='utf-8').decode('utf-8'))