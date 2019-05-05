# encoding: utf-8

import sys
import re
from workflow import Workflow, ICON_WEB, web
from workflow import (MATCH_ALL, MATCH_ALLCHARS, MATCH_ATOM, MATCH_CAPITALS, MATCH_INITIALS, MATCH_INITIALS_CONTAIN, MATCH_INITIALS_STARTSWITH, MATCH_STARTSWITH, MATCH_SUBSTRING)

LATEST_JSON = 'https://gist.githubusercontent.com/lilywang711/8449705fc664ae86e70d09295444a276/raw/86f8fcf21bdef4763828f75220072a1abe8f49ed/latest.json'
DOCS_BASE_URL = 'http://ramda.cn/docs/'

def unicodeize_arrow(s):
    return re.sub(r'->', u'→', s)

def format_title(function):
    name = function['name']
    if not function['sig']: return name
    sig  = unicodeize_arrow(function['sig'])
    return ' '.join([name, '::', sig])

def get_functions():
    r = web.get(LATEST_JSON)
    r.raise_for_status()
    return r.json()

def space_to_underscore(s):
    return re.sub(r' ', u'_', s)

def search_key_for_function(function):
    elements = []
    elements.append(function['name'])
    elements.append(space_to_underscore(function['sig']))
    return u' '.join(elements)

def main(wf):
    functions = wf.cached_data('functions', get_functions, max_age=3600)

    if len(wf.args) and wf.args[0]:
        query = space_to_underscore(re.sub(r'^R\.', u'', wf.args[0]))
    else:
        query = None

    if query:
        functions = wf.filter(query, functions, key=search_key_for_function,
                min_score=20, match_on=MATCH_STARTSWITH | MATCH_SUBSTRING)

    for f in functions:
        docs_url = "%s#%s" % (DOCS_BASE_URL, f['name'])
        wf.add_item(title=format_title(f),
                    subtitle=f['description'],
                    arg=docs_url,
                    valid=True,
                    icon='icon.png')

    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
