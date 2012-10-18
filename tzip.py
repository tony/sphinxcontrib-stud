# -*- encoding: utf8 -*-

"""A tzip directive for sphinx documenter"""

# guibog@gmail.com
#
# https://github.com/guibog/sphinx-tzip

import pprint
import os
import pickle
from docutils import nodes
from sphinx.util.compat import Directive

class TzDirective(Directive):
    required_arguments = 1
    def run(self):
        tzid, = self.arguments
        return [tz(tzid=tzid)]

class TzipDirective(Directive):
    required_arguments = 2
    def run(self):
        source, target_tzid = self.arguments
        return [tzip(source=source, target_tzid=target_tzid)]

class tz(nodes.Element):
    pass

class tzip(nodes.General, nodes.Element):
    pass

class WrongSourceDoctree():
    ids = []
    def __init__(self, err):
        self.err = err

def _load_source_doctree(env, source):
    path = os.path.join(env.doctreedir, "%s.doctree" % source)
    try:
        f = open(path)
        return pickle.load(f)
    except IOError, err:
        return WrongSourceDoctree(err)

def process_tzip(app, doctree, fromdocname):
    env = app.builder.env
    #pprint.pprint(env.__dict__)
    doctrees = {}
    for node in doctree.traverse(tzip):
        source = node.attributes['source']
        target_tzid = 'std:tz-' + node.attributes['target_tzid'].lower()
        if source not in doctrees:
            doctrees[source] = _load_source_doctree(env, source)
        if isinstance(doctrees[source], WrongSourceDoctree):
            err = "Unable to find source %s" % source
            doctree.reporter.warning(err, line=node.line)
            node.replace_self(nodes.problematic(err, err))
            return
        if target_tzid in doctrees[source].ids:
            contents = []
            # Go to next tz marker, excluded
            for n in doctrees[source].ids[target_tzid].traverse(
                    include_self=True, siblings=True, descend=False):
                if isinstance(n, nodes.target):
                    break
                contents.append(n)
            print "FOUND", len(contents), contents
            node.replace_self(contents)
        else:
            print doctrees[source].ids
            err = "Unable to find target %s in source %s" % (target_tzid, source)
            doctree.reporter.warning(err, line=node.line)
            node.replace_self(nodes.problematic(err, err))


def setup(app):
    app.add_node(tzip)
    app.add_crossref_type('tz', 'tz', 'single: %s', nodes.generated)
    app.add_directive('tzip', TzipDirective)
    app.connect('doctree-resolved', process_tzip)

