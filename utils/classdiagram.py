#!/usr/bin/env python
#
# classdiagram.py - Generates a class diagram of E:S
#
#    Copyright (C) 2012 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>
#
# If run as a script, creates a classes_singularity.png image file in current
# directory, containing a class diagram of all classes in E:S and their
# inheritance relationship.
#
# This module is importable as well. In this case, it only creates a Project
# instance pre-loaded (and resolved) with all E:S modules, imports and classes,
# ready to use.


#TODO:
# - create list of identifiers for each module. parse() or resolve() must
#   populate it. dict Module.objects = { name: obj }
# - dummy classes for ExternalModule, BuiltinClass, ExternalObject
# - get rid of Import/From classes. Once a module is parsed and resolved,
#   what I really need is the module namespace (object list) with identifiers
#   associated with either a Module, ExternalModule, Class, BuiltinClass
# - Module.import() and Module.importfrom() methods to be called from parse,
#   simulating python's import mechanism, resolving names and returning objects,
#   keeping list of externals and builtins in Project
# - whatever is the solution, respect name binding order in each code
# - resolve() (or whatever) should work in a way that a.b.c is imported as
#   a, then b, then c.
# - A walk() that yields a module per import/from would be great. Should have a
#   unused=False arg, that also yielded unreachable modules afterwards,
#   path-wise (default True for Project and Package)


import sys
import os.path
import re
import ast


class Node(object):
    """ Tree node that has a name, a parent, an associated file, and a list of
        modules. Currently used by Project and Module (and by proxy, Package) """

    def __init__(self, **kwargs):
        # The bucket stops here...
        if not hasattr(self,'name'):   self.name   = kwargs.pop('name'  , None)
        if not hasattr(self,'file'):   self.file   = kwargs.pop('file'  , None)
        if not hasattr(self,'parent'): self.parent = kwargs.pop('parent', None)

        self.modules = []

        # Add itself to parent
        if self.parent:
            self.parent.modules.append(self)

    @property
    def fullname(self):
        return self.parent.fullname+"."+self.name if self.parent else self.name

    def add_modules_by_path(self):

        ident = re.compile(r"^[^\d\W]\w*$")
        path = os.path.dirname(self.file)
        packagefile = "__init__.py"

        dirnames, filenames = os.walk(path).next()[1:]

        # Add modules
        for filename in sorted(filenames):
            name, ext = os.path.splitext(filename)
            if (ext == ".py" and
                filename != packagefile and
                re.match(ident, name)):
                Module(name=name,
                       file=os.path.join(path,filename),
                       parent=self)

        # Add packages
        for dirname in sorted(dirnames):
            if packagefile in os.walk(os.path.join(path,dirname)).next()[2]:
                Package(name=dirname,
                        file=os.path.join(path,dirname,packagefile),
                        parent=self)

    def get_all_modules(self):
        """ Returns a list of all modules in a Package (or Project),
        not including itself, recursively."""
        modules = []
        for module in self.modules:
            modules.append(module)
            modules.extend(module.get_all_modules())
        return modules

    def get_ancestors(self):
        if self.parent:
            return [self.parent] + self.parent.get_ancestors()
        else:
            return []

    #TODO: this can be *vastly* improved...
    def get_module_by_ref(self, ref):
        """ Returns a module instance by it's reference name. ref may be an
            absolute name, rooted at the topmost node (usually a Project), or
            relative (explicitly or implicitly) to the caller's hierarchy. """

        if self.parent:
            topmodule = self.get_ancestors()[-1]
            if ref.startswith("."):
                refs = [self.parent.fullname+ref]
            else:
                refs = [self.parent.fullname+"."+ref, ref]
        else:
            topmodule = self
            refs = [ref] if not ref.startswith(".") else [ref[1:]]

        for module in topmodule.get_all_modules():
            if module.fullname in refs:
                return module

    def print_tree(self, endent=0, **kwargs):
        print "{0}{1}".format("\t"*endent, self)
        for module in self.modules:
            module.print_tree(endent+1 if endent>=0 else -1, **kwargs)

    def __repr__(self):
        return "<{0}> {1}".format(type(self).__name__.lower(), self.fullname)


class Project(Node):

    def __init__(self,**kwargs):

        # Stores user-defined values, as opposed to calculated properties
        self._name  = None
        self._file  = None

        # No parent, by definition
        self.parent = None

        # User may or may not set name
        self.name   = kwargs.pop('name', None)

        # Set file<->path relationship (also based on name)
        path = kwargs.pop('path', None)
        file = kwargs.pop('file', None)
        if file:
            self.file(file, path)
        else:
            self.path = path

        # Node's init so far is a no-op for Project,
        # since name, file and parent are already set
        super(Project, self).__init__(**kwargs)
        super(Project, self).add_modules_by_path()

        # Set main (entry) module
        for module in self.modules:
            if module.file == self.file:
                self.main = module

        # Resolve modules. At first, only those reachable from main
        if self.main:
            self.main.isUsed = True
            self.main.resolve()

        # Now the unused ones
        for module in self.get_all_modules():
            module.resolve()

            # since we are here, also mark packages as used
            # if it has any used module
            if not module.isUsed:
                for mod in module.modules:
                    if mod.isUsed:
                        # mark ancestor packages too (except Project)
                        for anc in module.get_ancestors()[:-1]:
                            anc.isUsed = True
                        module.isUsed = True
                        break

    @property
    def name(self):
        """ Defined name or directory name or filename without extension """
        return (self._name or
                os.path.split(self.path)[1] or
                os.path.splitext(os.path.basename(self.file))[0])

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def path(self):
        """ Absolute path of entry file """
        if self.file:
            return os.path.dirname(os.path.abspath(self.file))
        else:
            return None

    @path.setter
    def path(self, value):

        #Check new directory
        if not os.path.isdir(value):
            raise ValueError("{0} is not a valid directory".format(value))

        # If path is already set, requires the same entry filename
        # to be present in the new directory
        if self.path:
            try:
                filename = os.path.basename(self.file)
                self.file = os.path.join(value, filename)
                return

            except ValueError:
                raise ValueError("Current entry filename {0}"
                                 " does not exist in {1}".format(filename,value))

        # Path is not set yet. Try to set it using either current project name
        # or new directory name as basename for entry file, trying each with
        # and without .py extension
        filenames = []
        for filename in [self.name, os.path.basename(value)]:
            if filename:
                filenames.extend([filename + ".py", filename])

        for filename in filenames:
            try:
                self.file = os.path.join(value, filename)
                return

            except ValueError:
                pass

        # We tried really hard...
        raise ValueError("No suitable entry filename {0}"
                         " found in {1}".format(set(filenames),value))

    @property
    def file(self):
        """ Project's entry file (__main__ module) """
        return self._file

    @file.setter
    def file(self, value, path=None):

        #If there is a directory component in entry, or if no path was given
        # (via __init__()),consider entry as it is
        # else, consider entry as a path+file

        filename = os.path.basename(value)

        if path and filename == value:
            filename = os.path.join(path, filename)
            message  = "{0} does not exist in {1}".format(filename, path)
        else:
            filename = value
            message  = "{0} does not exist".format(value)

        if os.path.isfile(filename):
            self._file = value
        else:
            raise ValueError(message)


class Module(Node):

    def __init__(self,**kwargs):
        self.classes    = kwargs.pop('classes',[])
        self.imports    = kwargs.pop('imports',[])
        self.isUsed     = False
        self.isResolved = False

        # Allow name to be optional
        if 'name' not in kwargs:
            self.name = os.path.splitext(os.path.basename(kwargs.get('file',
                                                                     None)))[0]

        super(Module, self).__init__(**kwargs)

        self.parse()

    @property
    def fullname(self):
        if isinstance(self.parent, Project):
            return self.name
        else:
            return super(Module, self).fullname

    def parse(self):
        self.classes = []
        self.imports = []
        with open(self.file) as source:

            #FIXME: such a simple loop will miss imports and classes declared
            #       inside a block (try/except, function, if, for, etc).
            for node in ast.parse(source.read()).body:

                # Add class
                if isinstance(node, ast.ClassDef):
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        if isinstance(base, ast.Attribute):
                            bases.append((base.value.id, base.attr))
                    Class(name=node.name, bases=bases, module=self)

                # Add import
                if isinstance(node, ast.Import):
                    for item in node.names:
                        Import(name=item.name, alias=item.asname, parent=self)

                # Add ImportFrom
                if isinstance(node, ast.ImportFrom):
                    for item in node.names:
                        ImportFrom(name=node.module, alias=item.asname,
                                   attribute=item.name, parent=self)

    def print_tree(self, endent=0,
                   show_imports=True, show_classes=True, show_external=True):
        print "{0}{1}".format("\t"*endent, self)

        if show_imports:
            for item in self.imports:
                if show_external or not getattr(item, 'external', False):
                    print "{0}{1}".format("\t"*(endent+1), item)

        if show_classes:
            for item in self.classes:
                print "{0}{1}".format("\t"*(endent+1), repr(item))

        for module in self.modules:
            module.print_tree(endent+1 if endent>=0 else -1,
                              show_imports, show_classes, show_external)

    def resolve(self):
        # As per the official import mechanism, load a module only once,
        # and consider it already loaded as soon as it begins processing,
        # not afterwards
        if self.isResolved:
            return
        else:
            self.isResolved = True

        # imports are resolved first (hopefully they appear first in code too)
        for imp in self.imports:
            imp.resolve()

        # then classes
        for cls in self.classes:
            cls.resolve()

    def get_object_by_name(self, name):
        """Resolve symbols in a module: given a name (symbol, identifier, etc),
        searches its Classes, Imports and ImportFroms and returns the associated
        object reference (which is an instance of Module or Class), or a string
        (for external modules and objects), or None if not found
        """
        for cls in self.classes:
            if cls.name == name:
                # Class
                return cls

        for imp in self.imports:
            if imp.bind == name:
                if imp.isExternal:
                    # External Module
                    return "<external module> %s" % name
                elif hasattr(imp, 'type'):
                    if imp.isModule or imp.isClass:
                        # Module or Class
                        return imp.reference
                    else:
                        # External Object
                        return "%s %s.%s" % (imp.type, imp.name, imp.attribute)
                else:
                    # Module
                    return imp.module

    def __repr__(self):
        return super(Module, self).__repr__() + (" <UNUSED>"
                                                 if not self.isUsed else "")


class Package(Module):

    def __init__(self,**kwargs):
        # Allow name to be optional
        if 'name' not in kwargs:
            self.name = os.path.basename(os.path.dirname(kwargs.get('file',
                                                                    None)))
        super(Package, self).__init__(**kwargs)
        super(Package, self).add_modules_by_path()


class Import(object):
    """An import in a module: import <name> as <alias>
    parent: a reference to the module containing the import line
    module: a reference to the imported module (or None)
    bind: string to imported module identifier in the importer (alias or name)
    isExternal: boolean for modules outside the project
    """
    # Facts (or, better, assumptions) about import x.y.z:
    # - x and y must be packages, z must be module or package
    # - no identifier reassignment in x or y can change z's binding
    # - thus, x.y.z will always mean either x/y/z.py or x/y/z/__init__.py
    # - current limitation: x must play nice about y, and both are nice about z

    def __init__(self, **kwargs):
        self.name       = kwargs.pop('name'  , None)
        self.alias      = kwargs.pop('alias' , None)
        self.parent     = kwargs.pop('parent', None)
        self.bind       = self.alias or self.name
        self.module     = None
        self.isExternal = True
        self.parent.imports.append(self)

    def resolve(self):
        module = self.parent.get_module_by_ref(self.name)
        if module:
            self.isExternal = False
            self.module = module
            # mark a module as used if the importer is also used
            if self.parent.isUsed:
                self.module.isUsed = True
            self.module.resolve()

    def __repr__(self):
        return "<{0}>{1} {2}{3}".format(
            type(self).__name__.lower(),
            " <external>" if self.isExternal else "",
            self.module or self.name,
            (" <as> %s" % self.alias) if self.alias else "",)


class ImportFrom(Import):
    """A from import in a module: from <name> import <attribute> as <alias>
    importfrom: convenience boolean to tell apart from plain Import's
    bind: string to imported attribute identifier in the importer (alias or attribute)
    type: string identifying the attribute type. May be one of:
          <ident>  - for unknown identifiers, either from external imports, as
                     in `from os import path`; or identifiers that are not
                     modules or classes, as in `from buyable import cash`
          <module> - for modules, as in from `code.graphics import g`
          <class>  - for classes, as in from `code.buyable import Buyable`
    is_*: convenience booleans to identify the attribute type
    reference: a reference to either a module or a class (None for other types)
    """

    # Facts (or, better, assumptions) about from x.y import z:
    # - same rules as Import applies to x.y: x/y.py or x/y/__init__.py
    # - z can be any identifier in y:
    #   import z, import k as z, from i.j import k as z, class z()
    # - if y is a package, z can also be a submodule/subpackage

    def __init__(self, **kwargs):
        self.attribute  = kwargs.pop('attribute', None)
        self.reference  = None
        self.type       = "<object>"
        self.isModule   = False
        self.isClass    = False

        super(ImportFrom, self).__init__(**kwargs)
        self.bind = self.alias or self.attribute


    def resolve(self):
        super(ImportFrom, self).resolve()

        # do not resolve attributes from external modules
        if self.isExternal:
            return

        # No breaks or returns from now on: any new reference found will
        # (and should) overwrite the previous definition

        # Search for attribute as module in a package
        # from code.graphics import g
        for mod in self.module.modules:
            if mod.name == self.attribute:
                self.reference = mod

        # Search for attribute as bind in import or importfrom in a module
        # Bind reference may be a module, class or object
        # from code.screens.map import g, gg, location, OptionsScreen, math, newaxis
        #   which may be found in code.screens.map as:
        #     from code import g                 # module
        #     from code.graphics import g as gg  # module
        #     import location                    # module
        #     from options import OptionsScreen  # class
        #     import math                        # object
        #     from numpy import newaxis          # object
        for imp in self.module.imports:
            if imp.bind == self.attribute:
                self.reference = getattr(imp, 'reference', imp.module)

        # Search for attribute as class in a module
        # (again, hopefully they come after imports)
        # from buyable import Buyable
        for cls in self.module.classes:
            if cls.name == self.attribute:
                self.reference = cls

        # Found a reference? Fill in the blanks...
        if self.reference:
            if isinstance(self.reference, Class):
                self.type = "<class>"
                self.isClass = True
            else:
                self.type = "<module>"
                self.isModule = True
                # mark the attribute module as used if the importer is also used
                if self.parent.isUsed:
                    self.reference.isUsed = True
                self.reference.resolve()

    def __repr__(self):
        if self.isExternal:
            return "<{0}> <external> {1} {2}{3}".format(
                type(self).__name__.lower(),
                self.name, self.attribute,
                (" <as> %s" % self.alias) if self.alias else "",)
        else:
            return "<{0}> {1} {2}{3}".format(
                type(self).__name__.lower(),
                self.module,
                self.reference or ("%s %s" % (self.type, self.attribute)),
                (" <as> %s" % self.alias) if self.alias else "",)


class Class(object):

    def __init__(self,**kwargs):
        self.name   = kwargs.pop('name'  , None)
        self.module = kwargs.pop('module', None)
        self.bases  = kwargs.pop('bases' , [])
        self.module.classes.append(self)

    def resolve(self):

        def find_class(module, name):
            for cls in module.classes:
                if cls.name == name:
                    return cls

        for i, base in enumerate(self.bases):

            if isinstance(base, tuple):
                mod, name = base
                obj = self.module.get_object_by_name(mod)
                if isinstance(obj, Module):
                    module = obj
                    builtins = False
                else:
                    if isinstance(obj, Class):
                        # mod is supposed to be a Module, not a known Class
                        self.bases[i] = "<NOTMODULE> %s in %s: %s" % (mod, base, obj)
                    elif obj:
                        # external module or object, as string
                        self.bases[i] = obj
                    else:
                        self.bases[i] = "<NOTFOUND> %s" % (base)

                    # for all cases, bail out
                    continue
            else:
                name = base
                module = self.module
                builtins = True

            cls = module.get_object_by_name(name)
            if cls:
                if isinstance(cls, Class):
                    self.bases[i] = cls
                else:
                    # currently, can only be a Module
                    self.bases[i] = "<NOTCLASS> %s in %s: %s" % (name, base, cls)
            else:
                if builtins:
                    self.bases[i] = "<builtin> %s" % name
                else:
                    self.bases[i] = "<NOTFOUND> %s in %s" % (name, base)

    def __repr__(self):
        bases = []
        for base in self.bases:
            if isinstance(base, Class):
                name = "<class> " + base.module.fullname + '.' + base.name
            else:
                name = base
            bases.append("%s" % name)

        return "<{0}> {1} ({2})".format(type(self).__name__.lower(),
                                        self.name,
                                        ", ".join(bases))



#TODO: besides the obvious, a cool idea: color-by-package (or module)
def generate_classdiagram(modules=None, project=None, modulenames=True,
                          builtins=True, externals=True):
    project = project or esproject
    modules = modules or set()

    if modules:
        mods = set()
        for module in modules:
            mod = project.get_module_by_ref(module)
            if mod:
                mods.add(mod)
                mods.update(mod.get_all_modules())
    else:
        mods = project.get_all_modules()

    def nodename(cls):
        if modulenames:
            return "%s.%s" % (cls.module.fullname, cls.name)
        else:
            return cls.name

    header = ("""\
digraph "%s" {
ranksep=.50;
nodesep=.50;
ratio=.20;
edge [arrowsize=.50];
node [shape=record,fontname=FreeSans,fontsize=7,height=.10,width=.10
      style=filled,fillcolor=white];
""" % project.name)
    footer = "}\n"

    nodes = []
    relations = []
    nonclasses = []

    for mod in sorted(mods):
        for cls in mod.classes:
            clsnodename = nodename(cls)
            nodes.append('"%s";\n' % clsnodename)
            for base in cls.bases:
                if isinstance(base, Class):
                    relations.append('"%s" -> "%s";\n' % (clsnodename,
                                                          nodename(base)))
                elif builtins and externals:
                    # define name
                    if modulenames:
                        nonclsnodename = "__builtin__." + base.partition("> ")[2]
                    else:
                        nonclsnodename = base.partition("> ")[2].split('.')[-1]

                    # insert as a node, if not done yet
                    if base not in nonclasses:
                        nonclasses.append(base)
                        nodes.append('"%s";\n' % nonclsnodename)

                    relations.append('"%s" -> "%s";\n' % (clsnodename,
                                                          nonclsnodename))

    with open("rodrigo.dot", 'w') as f:
        f.write(header)
        f.write("".join(nodes))
        f.write("".join(relations))
        f.write(footer)

    os.system("unflatten rodrigo.dot | dot -Tpng -o rodrigo.png && xdg-open rodrigo.png")




if __name__ != '__main__':
    # executed as module
    mydir = os.path.dirname(__file__)
    esdir = os.path.realpath(os.path.join(mydir,".."))
    esproject = Project(name="singularity", path=esdir)
    del(mydir)  # be tidy
else:
    if not os.path.basename(sys.argv[0]).startswith("classdiagram"):
        # executed indirectly as execfile() in pydev's console
        for esdir in sys.path:
            if os.path.basename(esdir) == "singularity":
                esproject = Project(name="singularity", path=esdir)
                break
    else:
        # executed directly as a script
        mydir = os.path.dirname(os.path.realpath(sys.argv[0]))
        esdir = os.path.realpath(os.path.join(mydir,".."))
        esproject = Project(name="singularity", path=esdir)

        # Fun things to do...
        #esproject.print_tree(show_imports=True, show_classes=True)
        #generate_classdiagram(['code.graphics','code.screens'], modulenames=True)
        generate_classdiagram(modulenames=True)


#FIXME: very old, not-yet-working code. Halfway conversion from a bash script
def bash_classparser():
    import argparse
    import subprocess

    def which(cmd, *noops):
        args=[cmd]
        if noops:
            args.extend([x for x in noops if x is not None])
        else:
            args.append("--help")
        try:
            subprocess.call(args)
            return True
        except OSError:
            return False

    argparser = argparse.ArgumentParser(description='Generates a class diagram of E:S.')
    argparser.add_argument('--format', default="png", help='output diagram format. Default is png')
    args = argparser.parse_args()
    format = args.format
    if format == "txt": print("'{0}' is not a valid format".format(format))
    tempfile = os.tmpfile()
    tempdir = os.path.dirname(tempfile.name)
    print("could not access source dir '"+esdir+"'")

    try:
        pass
    finally:
        tempfile.close()
