#!/usr/bin/env python
"""
Writes standard selection names for:
    - protein residues
    - protein backbone atoms
    - nucleic residues
    - nucleic backbone atoms
    - nucleobase atoms
    - nucleic sugar atoms
"""
from typing import Type

from base import TableWriter
from MDAnalysis.core import selection as sel


def _chunk_list(lst: list, chunk_size: int = 8) -> list:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


# override get_lines as there are no headings
def _generate_lines(
    *, klass: Type, attr: str, sort: bool = False, chunk_size: int = 8
) -> list[str]:
    selected = getattr(klass, attr)
    if sort:
        selected = sorted(selected)

    table = _chunk_list(list(selected), chunk_size=chunk_size)
    return table


class StandardSelectionTable:
    def __init__(self, filename, *args, **kwargs):

        self.table_writer = TableWriter(
            sort=False,
            filename="generated/selections/{}.txt".format(filename),
            generate_lines=_generate_lines,
        )
        self.table_writer.get_lines_and_write_table(*args, **kwargs)


if __name__ == "__main__":
    StandardSelectionTable(
        "protein", klass=sel.ProteinSelection, attr="prot_res", sort=True
    )
    StandardSelectionTable(
        "protein_backbone", klass=sel.BackboneSelection, attr="bb_atoms"
    )
    StandardSelectionTable("nucleic", klass=sel.NucleicSelection, attr="nucl_res")
    StandardSelectionTable(
        "nucleic_backbone", klass=sel.NucleicBackboneSelection, attr="bb_atoms"
    )
    StandardSelectionTable("base", klass=sel.BaseSelection, attr="base_atoms")
    StandardSelectionTable(
        "nucleic_sugar", klass=sel.NucleicSugarSelection, attr="sug_atoms"
    )
