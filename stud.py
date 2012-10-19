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

class StudDirective(Directive):
    required_arguments = 2
    option_spec = {
        'debug': directives.flag,
    }
    def run(self):
        source, target_tzid = self.arguments
        return [stud(source=source,
            target_tzid=target_tzid,
            debug='debug' in self.options)]

class st(nodes.Element):
    pass

class stud(nodes.General, nodes.Element):
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

class TranscluderVisitor(nodes.GenericNodeVisitor):
    target_id = None
    def default_visit(self, node):
        print "VV", node
        pass

def transclude_by_walking(tree, source, from_id, to_id, info, _id_prefix):
    if from_id not in tree.ids:
        return None
    target = tree.ids[from_id]
    contents = []
    info("stud extension: %s %s found target node" % (source, from_id))
    # Go to next st marker, excluded
    def is_a_target(node):
        return any(i.startswith(_id_prefix) for i in node.attributes['ids'])
    def is_this_target(node, tid):
        return tid in node.attributes['ids']
    for sibling in target.traverse(include_self=True, siblings=True, descend=False, ascend=False):
        # TODO, should use ascend=True but it includes main doctree elements, including studs ~~~
        for child in sibling.traverse(include_self=True, siblings=False, descend=True):
            if isinstance(child, nodes.Text):
                continue
#            info(">> %s %s" % (type(child), child))
            if is_a_target(child) and not is_this_target(child, from_id):
                info("stud extension: %s %s stopping before %s" % (source, from_id, child))
                break
            info("stud extension: %s %s adding %s" % (source, from_id, child))
            contents.append(child)
    else:
        info("stud extension: reached end of doctree")
    info("FOUND %s blocks" % len(contents))
    return contents
    #visi = TranscluderVisitor(maintree)

    #tree.walk(visi)
    return []

def process_stud(app, doctree, fromdocname):
    _id_prefix = 'std:st-'
    env = app.builder.env
    _keep_report_level = doctree.reporter.report_level
    info = doctree.reporter.info
    warn = doctree.reporter.warning
    #pprint.pprint(env.__dict__)
    doctrees = {}
    for node in doctree.traverse(stud):
        source = node.attributes['source']
        target_tzid = _id_prefix + node.attributes['target_tzid'].lower()
        if node.attributes['debug']:
            doctree.reporter.report_level = doctree.reporter.INFO_LEVEL
        else:
            doctree.reporter.report_level = _keep_report_level
        info("stud extension: studding %s %s" % (source, target_tzid), line=node.line)
        if source not in doctrees:
            doctrees[source] = _load_source_doctree(env, source)
        if isinstance(doctrees[source], WrongSourceDoctree):
            err = "Unable to find source %s" % source
            warn(err, line=node.line)
            node.replace_self(nodes.problematic(err, err))
            return
        if True:
            new_content = transclude_by_walking(doctrees[source], source, target_tzid, None, info, _id_prefix)
        if new_content is None:
            err = "Unable to find target %s in source %s" % (target_tzid, source)
            warn(err, line=node.line)
            node.replace_self(nodes.problematic(err, err))
        else:
            node.replace_self(new_content)

        continue
        
        

        # ----- trying fuill doc traverse
        #contents = []
        #inside = False
        #for n in doctrees[source].traverse():
        #    if isinstance(n, nodes.Text):
        #        continue
        #    if isinstance(n, nodes.section):
        #        continue
        #    if n.attributes.get('refid', '').startswith(_id_prefix):
        #        inside = False
        #    if n.attributes.get('refid') == target_tzid:
        #        inside = True
        #    info("%s %s" % (inside, n))
        #    if inside:
        #        contents.append(n)
        #    #if n.attributes
        #node.replace_self(contents)
        #continue

        # ---- trying pinpointing ids
        if target_tzid in doctrees[source].ids:
            target = doctrees[source].ids[target_tzid]
            contents = []
            info("stud extension: %s %s found target node" % (source, target_tzid))
            # Go to next st marker, excluded
            for sibling in target.traverse(include_self=True, siblings=True, descend=False):
                for child in sibling.traverse(include_self=True, siblings=False, descend=True):
                    if isinstance(child, nodes.Text):
                        continue
                    info(">> %s %s" % (type(child), child))
                    if (hasattr(child, 'attributes') and
                            any(i.startswith(_id_prefix) for i in child.attributes['ids'])):
                        info("stud extension: %s %s stopping before %s" % (source, target_tzid, child))
                        break
                    info("stud extension: %s %s adding %s" % (source, target_tzid, child))
                    contents.append(child)
            else:
                info("stud extension: reached end of doctree")
            info("FOUND %s blocks" % len(contents))
            node.replace_self(contents)
        else:
            err = "Unable to find target %s in source %s" % (target_tzid, source)
            warn(err, line=node.line)
            node.replace_self(nodes.problematic(err, err))
    doctree.reporter.report_level = _keep_report_level




def setup(app):
    app.add_config_value('stud_debug', False, False)
    app.add_node(stud)
    app.add_crossref_type('st', 'st', 'single: %s', nodes.generated)
    app.add_directive('stud', StudDirective)
    app.connect('doctree-resolved', process_stud)

