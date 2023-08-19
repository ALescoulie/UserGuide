#!/usr/bin/env python
"""
Generate topology_defaults.txt:

A table of whether TopologyAttrs are atomwise, residuewise, or segmentwise, and their defaults
"""

from base import TableWriter
from core import TOPOLOGY_CLS
from MDAnalysis.core.topologyattrs import AtomAttr, ResidueAttr, SegmentAttr

DEFAULTS = {
    "resids": "continuous sequence from 1 to n_residues",
    "resnums": "continuous sequence from 1 to n_residues",
    "ids": "continuous sequence from 1 to n_atoms",
}


def _atom(klass):
    return klass.attrname


def _atomgroup(klass):
    return klass.singular


def _default(klass):
    try:
        return DEFAULTS[klass.attrname]
    except KeyError:
        try:
            return repr(klass._gen_initial_values(1, 1, 1)[0])
        except NotImplementedError:
            return "No default values"


def _level(klass):
    if issubclass(klass, AtomAttr):
        level = "atom"
    elif issubclass(klass, ResidueAttr):
        level = "residue"
    elif issubclass(klass, SegmentAttr):
        level = "segment"
    else:
        raise ValueError
    return level


def _type(klass):
    return klass.dtype


class TopologyDefaults:
    def __init__(self) -> None:
        self.table_writer = TableWriter(
            filename="generated/topology/defaults.txt",
            headings=("Atom", "AtomGroup", "default", "level", "type"),
            sort=True,
            input_items=TOPOLOGY_CLS,
            columns={
                "Atom": _atom,
                "AtomGroup": _atomgroup,
                "default": _default,
                "level": _level,
                "type": _type,
            },
        )
        self.table_writer.get_lines_and_write_table()


if __name__ == "__main__":
    TopologyDefaults()
