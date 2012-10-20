# -*- encoding: utf8 -*-

"""A stud directive for sphinx documenter"""

# guibog@gmail.com
#
# https://github.com/guibog/sphinx-stud

import pprint
import os
import pickle
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive

isa = isinstance
_id_prefix = 'std:st-'

class StudDirective(Directive):
    required_arguments = 2
    option_spec = {
        'debug': directives.flag,
    }
    def run(self):
        source, target_id = self.arguments
        debug = 'debug' in self.options
        return [stud(source=source, target_id=target_id, debug=debug)]

class stud(nodes.General, nodes.Element):
    pass

class WrongSourceDoctree():
    pass

def _load_source_doctree(doctreedir, source, fromdocname):
    if source.startswith('./'):  # Relative source
        local_path = fromdocname[:fromdocname.rfind('/')]
        source = source[2:]
    else:
        local_path = ''
    path = os.path.join(doctreedir, local_path, "%s.doctree" % source)
    try:
        f = open(path)
        return pickle.load(f)
    except IOError:
        return WrongSourceDoctree()

def _transclude(tree, source, from_id, to_id, info):
    if from_id not in tree.ids:
        return None
    target = tree.ids[from_id]
    contents = []
    info("stud: %s %s found target node" % (source, from_id))
    for sibling in target.traverse(include_self=True, siblings=True,
                                   descend=False, ascend=True):
        # TODO, should use ascend=True but it includes main doctree elements,
        # including studs ~~~
        if _is_target(sibling, to_id) and not _is_target(sibling, from_id):
            info("stub: found next target, breaking %s" % sibling)
            break
        contents.append(_prune_next(sibling.deepcopy(), to_id))
    else:
        info("stud: reached end of doctree")
    return contents

def _prune_next(tree, to_id):
    new_children = []
    for child in tree.children:
        if _is_target(child, to_id):
            break
        new_children.append(_prune_next(child, to_id))
    tree.children = new_children
    return tree

def _is_target(node, to_id):
    if not isa(node, nodes.Element):
        return False
    if to_id:
        return to_id in node.attributes['ids']
    else:
        return any(i.startswith(_id_prefix) for i in node.attributes['ids'])

def process_stud(app, doctree, fromdocname):
    env = app.builder.env
    _keep_report_level = doctree.reporter.report_level
    info = doctree.reporter.info
    warn = doctree.reporter.warning
    doctrees = {}
    for node in doctree.traverse(stud):
        source = node.attributes['source']
        target_id = _id_prefix + node.attributes['target_id'].lower()
        if node.attributes['debug']:
            doctree.reporter.report_level = doctree.reporter.INFO_LEVEL
        else:
            doctree.reporter.report_level = _keep_report_level
        info("stud: studding %s %s" % (source, target_id))
        if source not in doctrees:
            doctrees[source] = _load_source_doctree(env.doctreedir, source, fromdocname)
        if isa(doctrees[source], WrongSourceDoctree):
            err = "Unable to find source %s" % source
            warn(err, line=node.line)
            node.replace_self(nodes.problematic(err, err))
            return
        new_content = _transclude(doctrees[source], source, target_id, None, info)
        if new_content is None:
            err = "Unable to find target %s in source %s" % (target_id, source)
            warn(err, line=node.line)
            node.replace_self(nodes.problematic(err, err))
        elif new_content is []:
            err = "Empty target %s in source %s" % (target_id, source)
            warn(err, line=node.line)
            node.replace_self([])
        else:
            node.replace_self(new_content)
    doctree.reporter.report_level = _keep_report_level

def setup(app):
    app.add_config_value('stud_debug', False, False)
    app.add_node(stud)
    app.add_crossref_type('st', 'st', 'single: %s', nodes.generated)
    app.add_directive('stud', StudDirective)
    app.connect('doctree-resolved', process_stud)
