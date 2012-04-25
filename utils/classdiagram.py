#!/usr/bin/env python

# Generates a class diagram of E:S in png format

import os.path
import re
import ast


class Node(object):
    """ Tree node that has a name, a parent, an associated file, and a list of
        modules. Currently used by Project and Module (and by proxy, Package) """

    _ident = re.compile(r"^[^\d\W]\w*$")

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

        path = os.path.dirname(self.file)
        packagefile = "__init__.py"

        dirnames, filenames = os.walk(path).next()[1:]

        # Add modules
        for filename in sorted(filenames):
            name, ext = os.path.splitext(filename)
            if (ext == ".py" and
                filename != packagefile and
                re.match(self._ident, name)):
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

        # Set main module
        for module in self.modules:
            if module.file == self.file:
                self.main = module

        # Resolve modules
        for module in self.get_all_modules():
            module.resolve()

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
        self.classes = kwargs.pop('classes',[])
        self.imports = kwargs.pop('imports',[])

        # Allow name to be optional
        if 'name' not in kwargs:
            self.name = os.path.splitext(os.path.basename(kwargs.get('file',
                                                                     None)))[0]

        super(Module, self).__init__(**kwargs)

        self.parse()

    @property
    def fullname(self):
        if isinstance(self.parent,Project):
            return self.name
        else:
            return super(Module,self).fullname

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

    def print_tree(self, endent=0, show_external=False):
        print "{0}{1}".format("\t"*endent, self)
        for item in sorted(self.imports) + self.classes:
            if show_external or not getattr(item, 'external', False):
                print "{0}{1}".format("\t"*(endent+1), item)
        for module in self.modules:
            module.print_tree(endent+1 if endent>=0 else -1)

    def resolve(self):
        for imp in self.imports:
            imp.resolve()

        for cls in self.classes:
            cls.resolve()


    #FIXME: very old, not-yet-working code
    def dump(self):
        out = ""
        if self.imports or self.classes:
            out += "#", self.package.name, self.filename

        def import_line(packages,modules):
            out = ""
            if packages: out = "from {0} ".format(".".join(packages))
            out += "import (0}".format(", ".join(modules))
            return out

        prev_packages = None
        modules = []
        for packages, module, alias in sorted(self.imports):

            if alias: module += " as {alias}".format(alias=alias)
            modules.append(module)

            #if modules: out += "import ".format(", ".join(modules))
            #
            #out += import_line(packages, modules)
            #prev_packages = []
            #modules = []
            #modules.append(module)
            #packages = item[0]
            #module =
            #_from = "from " + ".".join(item[0]) + " "
            #_import = "import " + ", ".join(item
            if packages is not prev_packages:
                if packages: out += "from {0} ".format(".".join(packages))
                out += "import "


class Package(Module):

    def __init__(self,**kwargs):
        # Allow name to be optional
        if 'name' not in kwargs:
            self.name = os.path.basename(os.path.dirname(kwargs.get('file',
                                                                    None)))
        super(Package, self).__init__(**kwargs)
        super(Package, self).add_modules_by_path()


class Import(object):

    def __init__(self, **kwargs):
        self.name       = kwargs.pop('name'  , None)
        self.alias      = kwargs.pop('alias' , None)
        self.parent     = kwargs.pop('parent', None)
        self.module     = None
        self.external   = False
        self.parent.imports.append(self)

    @property
    def bind(self):
        return self.alias or self.name

    def resolve(self):
        module = self.parent.get_module_by_ref(self.name)
        if module:
            self.module = module
        else:
            self.external = True


    def __repr__(self):
        return "<{0}>{1} {2} <bind> {3}".format(type(self).__name__.lower(),
                                                " <external>"
                                                    if self.external else "",
                                                self.module or self.name,
                                                self.bind,
                                                )


class ImportFrom(Import):

    def __init__(self, **kwargs):
        self.attribute = kwargs.pop('attribute', None)
        self.type = None
        super(ImportFrom, self).__init__(**kwargs)

    @property
    def bind(self):
        return self.alias or self.attribute

    def resolve(self):
        super(ImportFrom, self).resolve()

        self.type = "<object> %s" % self.attribute

        if self.module:
            attribute = self.parent.get_module_by_ref(self.name + '.' + self.attribute)
            if attribute:
                self.type = attribute


    def __repr__(self):
        return "<{0}>{1} {2} {3} <bind> {4}".format(type(self).__name__.lower(),
                                                    " <external>"
                                                        if self.external else "",
                                                    self.module or self.name,
                                                    self.type,
                                                    self.bind,)


class Class(object):

    def __init__(self,**kwargs):
        self.name   = kwargs.pop('name'  , None)
        self.module = kwargs.pop('module', None)
        self.bases  = kwargs.pop('bases' , [])
        self.module.classes.append(self)

    def resolve(self):
        pass

    def __repr__(self):
        return "<{0}> {1} {2}".format(type(self).__name__.lower(),
                                      self.name,
                                      self.bases)


if __name__ == '__main__':
    import sys
    if os.path.basename(sys.argv[0]).startswith("classdiagram"):
        # executed directly as a script
        mydir = os.path.dirname(os.path.realpath(sys.argv[0]))
        esdir = os.path.realpath(os.path.join(mydir,".."))
        project = Project(name="singularity", path=esdir)
        project.print_tree(show_external=False)
    else:
        # executed indirectly as execfile() in pydev's console
        for dir in sys.path:
            if os.path.basename(dir) == "singularity":
                project = Project(name="singularity", path=dir)
                break
else:
    # executed as module
    mydir = os.path.dirname(__file__)
    esdir = os.path.realpath(os.path.join(mydir,".."))
    project = Project(name="singularity", path=esdir)


#FIXME: very old, not-yet-working code. Halfway conversion from a bash script
def bash_classparser():
    import argparse
    import subprocess
    myname =  os.path.basename(sys.argv[0])
    def fatal(msg="",code=-1):
        if msg: sys.stderr.write("error: {0}\n".format(msg))
        raise SystemExit(code)

    def error(msg=""):
        if msg: sys.stderr.write("error: {0}\n".format(msg))

    def which(cmd, *noops):
        args=[cmd]
        if noops:
            args.extend([x for x in noops if x is not None])
        else:
            args.append("--help")
        try:
            fnull = open(os.devnull, 'w')
            subprocess.call(args, stdout=fnull,stderr=fnull)
            fnull.close()
            return True

        except OSError: return False

    def requires(cmd, *noops, **kwargs):
        msg = kwargs.pop('msg',"")
        if msg: msg=", {0}".format(msg)
        else: msg="."
        which(cmd,*noops) or fatal("{0} requires '{1}'{2}".format(myname,cmd,msg))


    argparser = argparse.ArgumentParser(description='Generates a class diagram of E:S.')
    argparser.add_argument('--format', default="png", help='output diagram format. Default is png')
    args = argparser.parse_args()
    format = args.format
    if format == "txt": fatal("'{0}' is not a valid format".format(format))
    requires("pyreverse",msg="found in pylint package")
    tempfile = os.tmpfile()
    tempdir = os.path.dirname(tempfile.name)
    #classes = "classes_{0}.txt".format(project.name)
    #diagram = "classes_{0}.{1}".format(project.name,format)

    # Create a file will all classes from E:S
    os.chdir(esdir) or fatal("could not access source dir '"+esdir+"'")

    # Pyreverse requires current dir be source dir
    os.chdir(tempdir) or fatal("could not access temp dir '"+tempdir+"'")

    # Generate the Diagram
    #    pyreverse --only-classnames      \
    #              --all-ancestors        \
    #              --show-associated=0    \
    #              --module-names=n       \
    #              --project=singularity  \
    #              --output="$format"     \
    #              "$tempfile"

    #    if mv "$tempfile" "${esdir}/${classes}" and mv "$diagram"  "${esdir}":
    #        print "$self: generated '${classes}' and '${diagram}'"
    #    else:
    #        print "$self: generated '${tempfile}' and '${diagram}'"

    try:
        pass
    finally:
        tempfile.close()
