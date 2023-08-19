#!/usr/bin/env python
"""
Generate groupmethods.txt:

A table of transplanted methods.
"""

from collections import defaultdict

import base
from base import TableWriter
from core import TOPOLOGY_CLS
from MDAnalysis.core.groups import GroupBase


def _generate_input_items():
    items = []
    for klass in TOPOLOGY_CLS:
        for name, method in klass.transplants[GroupBase]:
            items.append([name, klass, method])
    return [x[1:] for x in sorted(items)]


def _method(klass, method):
    return base.sphinx_method(meth=method)


def _description(klass, method):
    return " ".join(method.__doc__.split(".\n")[0].split())


def _requires(klass, method):
    return klass.attrname


class TransplantedMethods:
    def __init__(self) -> None:
        self.table_writer = TableWriter(
            headings=["Method", "Description", "Requires"],
            filename="generated/topology/groupmethods.txt",
            input_items=_generate_input_items(),
            columns={
                "Method": _method,
                "Description": _description,
                "Requires": _requires,
            },
        )
        self.table_writer.get_lines_and_write_table()


if __name__ == "__main__":
    TransplantedMethods()
