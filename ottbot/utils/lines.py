# -*- coding=utf-8 -*-
"""Count the sourcecode lines of the Bot."""
from pathlib import Path

from pygount import ProjectSummary, SourceAnalysis

from ottbot.utils.embeds import FieldsT


def get_source_info() -> FieldsT:
    """Get the sourcecode breakdown of the project."""
    fields: FieldsT = []

    # py_files = [str(p) for p in Path(".").glob("ottbot/**/*.py")]
    # sql_files = [str(p) for p in Path(".").glob("ottbot/**/*.sql")]
    sql_files = []
    py_files = []

    summary = ProjectSummary()
    for file in py_files + sql_files:
        summary.add(SourceAnalysis.from_file(file, "pygount"))

    for lang_summary in summary.language_to_language_summary_map.values():
        fields.append(
            (
                lang_summary.language,
                f"{lang_summary.code_percentage}\n{lang_summary.documentation_percentage}\n{lang_summary.empty_percentage}",
                True,
            )
        )
    fields.append(
        (
            "Total",
            f"{summary.total_code_percentage}\n{summary.total_documentation_percentage}\n{summary.total_empty_percentage}",
            False,
        )
    )
    return fields


# class Lines:
#     """Analyzes the bots source code."""
#
#     def __init__(self) -> None:
#         self.py = [str(p) for p in Path(".").glob("ottbot/**/*.py")]
#         self.sql = [str(p) for p in Path(".").glob("ottbot/**/*.sql")]
#         self.targets = self.py + self.sql
#
#     def __len__(self) -> int:
#         return len(self.targets)
#
#     def grab_percents(self) -> tuple[float, float, float]:
#         """returns (code, docs, blank) percentages."""
#         code_p = self.code / self.total * 100
#         docs_p = self.docs / self.total * 100
#         blank_p = self.blank / self.total * 100
#         return round(code_p, 2), round(docs_p, 2), round(blank_p, 2)
#
#     def count(self) -> None:
#         """Counts the code in each file."""
#         data = ProjectSummary()
#
#         for file in self.targets:
#             analysis = SourceAnalysis.from_file(file, "pygount")
#             data.add(analysis)
#
#         self.code = data.total_code_count + data.total_string_count
#         self.docs = data.total_documentation_count
#         self.blank = data.total_empty_count
#         self.total = data.total_line_count
