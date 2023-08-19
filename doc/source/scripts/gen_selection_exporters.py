#!/usr/bin/env python
"""
Generates:
    - ../formats/selection_exporters.txt
"""

from typing import Type

import base
from base import TableWriter
from MDAnalysis import _SELECTION_WRITERS

SELECTION_DESCRIPTIONS = {
    "vmd": "VMD macros, available in Representations",
    "pml": "PyMOL selection string",
    "ndx": "GROMACS index file",
    "str": "CHARMM selection of individual atoms",
    "spt": "Jmol selection commands",
}


def _program(klass: Type) -> str:
    # classes have multiple formats.
    # First tends to be the program name, second is extension
    p = klass.format
    if isinstance(p, (list, tuple)):
        p = p[0]
    return base.sphinx_link(txt=p)


def _extension(klass: Type) -> str:
    return klass.ext


def _description(klass: Type) -> str:
    return SELECTION_DESCRIPTIONS[klass.ext]


def _class(klass):
    return base.sphinx_class(klass=klass, tilde=False)


class SelectionExporterWriter:
    def __init__(self) -> None:
        self.table_writer = TableWriter(
            headings=["Program", "Extension", "Description", "Class"],
            filename="formats/selection_exporter_formats.txt",
            include_table="Supported selection exporters",
            sort=True,
            input_items=set(_SELECTION_WRITERS.values()),
            columns={
                "Program": _program,
                "Extension": _extension,
                "Description": _description,
                "Class": _class,
            },
        )
        self.table_writer.get_lines_and_write_table()


if __name__ == "__main__":
    SelectionExporterWriter()
