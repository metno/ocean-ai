# Written by: Jostein Brandshoi, josteinb@met.no
# ===============================================
# Code for aiding the use of fimex config options.

import os
import re
import subprocess
import collections

class FimexConfig(object):
    """
    Class for representing the configuration setup for fimex. Lets you add, remove,
    read and write fimex options as well as running fimex with the specified options

    Example usage:
    > cfg = FimexConfig()
    > cfg.read_cfg("test.cfg")
    > cfg.addattr("input", "config", "kdejff.ncml")
    > cfg.addattr("extract", "selectVariables", "forecast_reference_time")
    > cfg.addattr("extract", "selectVariables", "Qair")
    > cfg.addattr("merge", "smoothing", "LINEAR(15,2)")
    > cfg.delattr("extract", "selectVariables", "Qair")
    > cfg.run_fimex(wait=True)
    > #cfg.write_cfg("test2.cfg")
    """

    def __init__(self):
        """Constructor defining attribute to hold all config info."""
        self.config = collections.OrderedDict()  # to be dict of dicts

    def read_cfg(self, filename):
        """
        Method to read an existing fimex config file and fill in the self.config
        dict attribute. The dict gets filled in the following sense;
        {"input": {"file": "filename.nc", "type": "netcdf"}, "extract": {...}}

        Args:
            filenam (str) : Name of existing fimex cfg file
        """
        category = None

        with open(filename, mode="r") as f:
            for line in f:
                category_match = re.match("\[.+\]", line)
                attr_match = re.match("[^#]*=[^#]*", line)

                if category_match:
                    category = category_match.group(0)[1:-1].strip()
                    self.addcategory(category)

                elif attr_match and category is not None:
                    match_str = attr_match.group(0)
                    eq_idx = match_str.index("=")
                    name = match_str[:eq_idx].strip()
                    value = match_str[eq_idx+1:].strip()
                    self.addattr(category, name, value)

    def addcategory(self, category):
        """
        Method that adds a category key (if it does not exist) to the self.config
        dict, to be filled with attributes later if wanted.

        Args:
            category (str) : Name of category to add
        """
        if category not in self.config.keys():
            self.config[category] = list()

    def delcategory(self, category):
        """
        Method to remove a fimex category from the self.config dict. Raises
        ValueError if category does not exist.

        Args:
            category (str) : Name of category to remove
        """
        if category not in self.config.keys():
            raise ValueError("Category {} does not exist!".format(category))

        del self.config[category]

    def addattr(self, category, name, value, overwrite=False):
        """
        Method adding a config attribute to the self.config dict (replacing
        it if it already exists if user wants to overwrite).

        Args:
            category (str) : Which fimex category to add the attribute to
            name (str)     : Name of attribute to add
            value (str)    : Value of attribute to add
        """
        self.addcategory(category)  # add category if it does not exist
        
        # check if only name matches to existing and delete if ovewrite
        if overwrite:
            for i, existing in enumerate(self.config[category]):
                if name == existing[0]:
                    del self.config[category][i]
                    break
            
        self.config[category].append((name, value))

        
    def delattr(self, category, name, value):
        """
        Method that removes an attribute from the self.config dict. Raises ValueError
        if either the specified category or attribute name does not exist.

        Args:
            category (str) : Which fimex category to remove an attribute from
            name (str)     : Name of attribute to remove
        """
        if category not in self.config.keys():
            raise ValueError("Category {} does not exist!".format(category))
        elif (name, value) not in [(n,v) for n,v in self.config[category]]:
            raise ValueError("Attribute {}={} does not exist in category {}!".format(name, value, category))

        self.config[category].remove((name, value))

        if not self.config[category]:
            self.delcategory(category)  # remove empty category

    def write_cfg(self, filename):
        """
        Method that writes a fimex cfg file based on the contents of the
        self.config dicts.

        Args:
            filename (str) : Name of file to write to
        """
        with open(filename, mode="w") as f:
            for c, d in self.config.items():
                f.write("\n[{}]\n".format(c))

                for name, value in d:
                    f.write("{}={}\n".format(name, value))

    def run_fimex(self, cfg_file=None, wait=True, fimex_executable='fimex', fimex_args=[], fimex_kwargs={}, debug=False, timeit=False):
        """
        Method that runs fimex with options as in the self.config dict. Either runs it
        directly from the commmand line by expaning the dict or lets you run it with a
        previously written fimex cfg file. Has the option to wait for subprocess to
        finish or to return a running subprocess without waiting.

        Args:
            cfg_file (str)      : Filename of fimex config file (defauts to None)
            wait (bool)         : Whether to use subprocess.call (waiting) or Popen (non-waiting)
            fimex_args (list)   : List of arguments to provide fimex (e.g. --debug)
            fimex_kwargs (dict) : Dict of arguments to provide fimex (e.g. -n 4)
            debug (bool)        : Enable debug mode for both this method and fimex
            timeit (bool)       : Enable linux timing of fimex command
        Returns:
            process (process) : If wait=False, returns the running Popen() process
        """
        fimex_args = fimex_args.copy()  # to avoid writing to sam memory if function claled several times
        fimex_kwargs = fimex_kwargs.copy()  # to avoid writing to sam memory if function claled several times
        fimex_args += ["--debug"] if debug else fimex_args
        fimex_args = " ".join(a for a in fimex_args)
        fimex_kwargs = " ".join("{} {}".format(k, v) for k,v in fimex_kwargs.items())
        cmd_string = "time " if timeit else ""
        cmd_string += "{} {} {}".format(fimex_executable, fimex_args, fimex_kwargs)

        if cfg_file is None:
            for category, attrs in self.config.items():
                for name, value in attrs:
                    cmd_string += " --{}.{}=\"{}\"".format(category, name, value)
        else:
            if not os.path.exists(cfg_file):
                raise IOError("File {} does not exist!".format(cfg_file))

            cmd_string += " -c {}".format(cfg_file)

        if debug:
            print("DEBUG from FimexConfig.run_fimex: {}".format(cmd_string))
        if not wait:
            return subprocess.Popen(cmd_string, shell=True)
        elif subprocess.call(cmd_string, shell=True):
            raise RuntimeError("Command {} failed!".format(cmd_string))
