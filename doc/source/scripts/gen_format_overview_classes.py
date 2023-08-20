#!/usr/bin/env python
"""
Generates:
    - ../formats/format_overview.txt : table of format overview
    - ../formats/coordinate_readers.txt: Coordinate reader information
    - ../formats/classes/*.txt : small tables of parser/reader/writer classes for each format
"""

from collections import defaultdict

import base
from base import TableWriter
from core import DESCRIPTIONS
from MDAnalysis import _CONVERTERS, _PARSERS, _READERS, _SINGLEFRAME_WRITERS

FILE_TYPES = defaultdict(dict)

for clstype, dct in (
    ("Coordinate reader", _READERS),
    ("Coordinate writer", _SINGLEFRAME_WRITERS),
    ("Topology parser", _PARSERS),
    ("Converter", _CONVERTERS),
):
    for fmt, klass in dct.items():
        if fmt in ("CHAIN", "MEMORY", "MINIMAL", "NULL"):
            continue  # get their own pages
        FILE_TYPES[fmt][clstype] = klass

sorted_types = sorted(FILE_TYPES.items())

SUCCESS = "\u2713"  # checkmark
FAIL = ""


def _keys(fmt, handlers):
    if fmt in DESCRIPTIONS:
        key = fmt
    else:
        key = list(handlers.values())[0].format[0]

        # raise an informative error
        if key not in DESCRIPTIONS:
            key = fmt
    return key


def _file_type(fmt, handlers, key):
    return base.sphinx_ref(txt=fmt, label=key, suffix="-format")


def _description(fmt, handlers, key):
    return DESCRIPTIONS[key]


class FormatOverview:
    def __init__(self) -> None:
        def _topology(fmt, handlers, key):
            if "Topology parser" in handlers:
                return SUCCESS
            return FAIL

        def _coordinates(fmt, handlers, key):
            if "Coordinate reader" in handlers:
                return SUCCESS
            return FAIL

        def _read(fmt, handlers, key):
            return SUCCESS

        def _write(fmt, handlers, key):
            if "Coordinate writer" in handlers:
                return SUCCESS
            if "Converter" in handlers:
                return SUCCESS
            return FAIL

        input_items = [
            (format, handlers, _keys(format, handlers))
            for format, handlers in sorted_types
        ]

        self.table_writer = TableWriter(
            filename="formats/format_overview.txt",
            include_table="Table of all supported formats in MDAnalysis",
            headings=[
                "File type",
                "Description",
                "Topology",
                "Coordinates",
                "Read",
                "Write",
            ],
            input_items=input_items,
            columns={
                "File type": _file_type,
                "Description": _description,
                "Topology": _topology,
                "Coordinates": _coordinates,
                "Read": _read,
                "Write": _write,
            },
        )
        self.table_writer.get_lines_and_write_table()


class CoordinateReaders:
    def __init__(self) -> None:
        def _velocities(fmt, handlers, key):
            if handlers["Coordinate reader"].units.get("velocity", None):
                return SUCCESS
            return FAIL

        def _forces(fmt, handlers, key):
            if handlers["Coordinate reader"].units.get("force", None):
                return SUCCESS
            return FAIL

        input_items = [
            (format, handlers, _keys(format, handlers))
            for format, handlers in sorted_types
            if "Coordinate reader" in handlers
        ]
        self.table_writer = TableWriter(
            filename="formats/coordinate_readers.txt",
            include_table="Table of supported coordinate readers and the information read",
            headings=["File type", "Description", "Velocities", "Forces"],
            input_items=input_items,
            columns={
                "File type": _file_type,
                "Description": _description,
                "Velocities": _velocities,
                "Forces": _forces,
            },
        )
        self.table_writer.get_lines_and_write_table()


class SphinxClasses(TableWriter):
    filename = "formats/reference/classes/{}.txt"

    def __init__(self, fmt):
        self.filename = self.filename.format(fmt)
        self.fmt = fmt
        super(SphinxClasses, self).__init__()

    def get_lines(self):
        lines = []
        for label, klass in sorted(FILE_TYPES[self.fmt].items()):
            lines.append(
                ["**{}**".format(label), self.sphinx_class(klass, tilde=False)]
            )
        self.lines = lines


if __name__ == "__main__":
    ov = FormatOverview()
    CoordinateReaders()
    for key in set(ov.fields["keys"]):
        SphinxClasses(key)
