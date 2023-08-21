#!/usr/bin/env python
"""
Generate three tables:
    - connectivityattrs.txt: A table of supported formats for bonds, angles, dihedrals, impropers
    - topologyattrs.txt: A table of supported formats for non-connectivity attributes.
    - topology_parsers.txt: A table of all formats and the attributes they read and guess

This script imports the testsuite, which tests these.
"""
import os
import sys
from collections import defaultdict

import base
from base import TableWriter
from core import DESCRIPTIONS, NON_CORE_ATTRS
from MDAnalysisTests.topology.base import mandatory_attrs
from MDAnalysisTests.topology.test_crd import TestCRDParser
from MDAnalysisTests.topology.test_dlpoly import (
    TestDLPConfigParser,
    TestDLPHistoryParser,
)
from MDAnalysisTests.topology.test_dms import TestDMSParser
from MDAnalysisTests.topology.test_fhiaims import TestFHIAIMS
from MDAnalysisTests.topology.test_gms import GMSBase
from MDAnalysisTests.topology.test_gro import TestGROParser
from MDAnalysisTests.topology.test_gsd import TestGSDParser
from MDAnalysisTests.topology.test_hoomdxml import TestHoomdXMLParser
from MDAnalysisTests.topology.test_lammpsdata import LammpsBase, TestDumpParser
from MDAnalysisTests.topology.test_mmtf import TestMMTFParser
from MDAnalysisTests.topology.test_mol2 import TestMOL2Base
from MDAnalysisTests.topology.test_pdb import TestPDBParser
from MDAnalysisTests.topology.test_pdbqt import TestPDBQT
from MDAnalysisTests.topology.test_pqr import TestPQRParser
from MDAnalysisTests.topology.test_psf import PSFBase
from MDAnalysisTests.topology.test_top import TestPRMParser
from MDAnalysisTests.topology.test_tprparser import TPRAttrs
from MDAnalysisTests.topology.test_txyz import TestTXYZParser
from MDAnalysisTests.topology.test_xpdb import TestXPDBParser
from MDAnalysisTests.topology.test_xyz import XYZBase

PARSER_TESTS = (
    TestCRDParser,
    TestDLPHistoryParser,
    TestDLPConfigParser,
    TestDMSParser,
    TestFHIAIMS,
    GMSBase,
    TestGROParser,
    TestGSDParser,
    TestHoomdXMLParser,
    LammpsBase,
    TestMMTFParser,
    TestMOL2Base,
    TestPDBParser,
    TestPDBQT,
    TestPQRParser,
    PSFBase,
    TestPRMParser,
    TPRAttrs,
    TestTXYZParser,
    TestXPDBParser,
    XYZBase,
    TestDumpParser,
)


MANDATORY_ATTRS = set(mandatory_attrs)

parser_attrs = {}


for p in PARSER_TESTS:
    expected, guessed = set(p.expected_attrs) - MANDATORY_ATTRS, set(p.guessed_attrs)
    # clunky hack for PDB
    if p is TestPDBParser:
        expected.add("elements")
    parser_attrs[p.parser] = (expected, guessed)


class TopologyParsers:
    def __init__(self):
        def _keys(parser, *args) -> tuple[str, str]:
            f = parser.format
            if isinstance(f, (list, tuple)):
                key = f[0]
                label = ", ".join(f)
            else:
                key = label = f
            return (key, label)

        def _description(parser, expected, guessed, key_label):
            key, label = key_label
            return DESCRIPTIONS[key]

        def _format(parser, expected, guessed, key_label):
            key, label = key_label
            return base.sphinx_ref(txt=label, label=key, suffix="-format")

        def _attributes_read(parser, expected, guessed, key_label):
            vals = sorted(expected - guessed)
            return ", ".join(vals)

        def _attributes_guessed(parser, expected, guessed, key_label):
            return ", ".join(sorted(guessed))

        input_items = [
            [parser, *attributes, _keys(parser=parser)]
            for parser, attributes in parser_attrs.items()
        ]
        self.table_writer = TableWriter(
            headings=["Format", "Description", "Attributes read", "Attributes guessed"],
            filename="formats/topology_parsers.txt",
            include_table="Table of supported topology parsers and the attributes read",
            sort=True,
            input_items=input_items,
            columns={
                "Format": _format,
                "Description": _description,
                "Attributes read": _attributes_read,
                "Attributes guessed": _attributes_guessed,
            },
        )
        self.table_writer.get_lines_and_write_table()

        attrs = defaultdict(set)

        def _get_attrs(line, format, parser, expected, guessed, key_label):
            for attribute in expected | guessed:
                attrs[attribute].add(format)

        [
            _get_attrs(line, format, *args)
            for line, format, args in zip(
                self.table_writer.lines,
                self.table_writer.fields["Format"],
                input_items,
            )
        ]
        self.attrs = attrs


class TopologyAttrs:
    def __init__(self, attrs):
        def _atom(name, singular, *args):
            return singular

        def _atomgroup(name, *args):
            return name

        def _description(name, singular, description):
            return description

        def _supported_formats(name, singular, description):
            return ", ".join(sorted(attrs[name]))

        input_items = sorted(
            [x, *y] for x, y in NON_CORE_ATTRS.items() if x not in MANDATORY_ATTRS
        )
        self.table_writer = TableWriter(
            headings=("Atom", "AtomGroup", "Description", "Supported formats"),
            filename="generated/topology/topologyattrs.txt",
            input_items=input_items,
            columns={
                "Atom": _atom,
                "AtomGroup": _atomgroup,
                "Description": _description,
                "Supported formats": _supported_formats,
            },
        )
        self.table_writer.get_lines_and_write_table()


class ConnectivityAttrs:
    def __init__(self, attrs) -> None:
        def _atom(name, singular, *args):
            return singular

        def _atomgroup(name, *args):
            return name

        def _supported_formats(name, singular, description):
            return ", ".join(sorted(attrs[name]))

        input_items = [[x] * 3 for x in ("bonds", "angles", "dihedrals", "impropers")]
        self.table_writer = TableWriter(
            headings=("Atom", "AtomGroup", "Supported formats"),
            filename="generated/topology/connectivityattrs.txt",
            input_items=input_items,
            columns={
                "Atom": _atom,
                "AtomGroup": _atomgroup,
                "Supported formats": _supported_formats,
            },
        )
        self.table_writer.get_lines_and_write_table()


if __name__ == "__main__":
    top = TopologyParsers()
    TopologyAttrs(top.attrs)
    ConnectivityAttrs(top.attrs)
