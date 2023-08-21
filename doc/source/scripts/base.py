from __future__ import print_function

import collections
import os
import pathlib
import sys
import textwrap
from collections import defaultdict
from typing import Callable, Iterable, Optional, Type

import tabulate


def _sanitize_method_name(name: str) -> str:
    return "_" + name.replace(" ", "_").replace("/", "_").lower()


class TableWriter:
    """
    For writing tables with easy column switching.

    Define _set_up_input() and column methods.

    Filename relative to source.
    """

    def __init__(
        self,
        headings: Iterable[str] = tuple(),
        filename: str = "",
        include_table: Optional[str] = None,
        sort: bool = True,
        input_items: Iterable = set(),
        columns: dict = {},
        generate_lines: Optional[Callable] = None,
    ):
        stem = os.getcwd().split("source")[0]
        self.path = os.path.join(stem, "source", filename)
        self.fields: dict[str, list[str]] = defaultdict(list)
        self.headings = headings
        self.filename = filename
        self.include_table = include_table
        self.sort = sort
        self.input_items = input_items
        self.columns = columns
        self.generate_lines = generate_lines

    def get_lines_and_write_table(self, *args, **kwargs):
        parent_directory = pathlib.Path(self.path).parent
        parent_directory.mkdir(exist_ok=True, parents=True)
        if self.generate_lines:
            self.lines = self.generate_lines(*args, **kwargs)
        else:
            self.get_lines(*args, **kwargs)
        self.write_table()

    def _run_method(self, method, *args, **kwargs):
        sanitized = _sanitize_method_name(method)
        meth = (
            self.columns[method] if method in self.columns else getattr(self, sanitized)
        )
        val = meth(*args, **kwargs)
        self.fields[method].append(val)
        return val

    def get_lines(self, *args, **kwargs):
        lines = []
        for items in self.input_items or self._set_up_input():
            line = (
                self.get_line(*items)
                if isinstance(items, collections.Iterable)
                else self.get_line(items)
            )
            lines.append(line)
        if self.sort:
            lines = sorted(lines)
        self.lines = lines

    def get_line(self, *args):
        line = []
        for h in self.headings:
            line.append(self._run_method(h, *args))
        return line

    def write_table(self):
        with open(self.path, "w") as f:
            f.write(f'..\n    Generated by {sys.argv[0].split("/")[-1]}\n\n')
            if self.include_table:
                f.write(f".. table:: {self.include_table}\n\n")
            tabled = tabulate.tabulate(
                self.lines, headers=self.headings, tablefmt="rst"
            )
            if self.include_table:
                tabled = textwrap.indent(tabled, "    ")
            f.write(tabled)
        print("Wrote ", self.filename)


# ==== HELPER FUNCTIONS ==== #


def sphinx_class(*, klass: Type, tilde: bool = True) -> str:
    prefix = "~" if tilde else ""
    return ":class:`{}{}.{}`".format(prefix, klass.__module__, klass.__name__)


def sphinx_method(*, meth: Callable, tilde: bool = True) -> str:
    prefix = "~" if tilde else ""
    return ":meth:`{}{}.{}`".format(prefix, meth.__module__, meth.__qualname__)


def sphinx_ref(*, txt: str, label: Optional[str] = None, suffix: str = "") -> str:
    return f":ref:`{txt} <{label}{suffix}>`"


def sphinx_link(*, txt: str) -> str:
    return "`{}`_".format(txt)
