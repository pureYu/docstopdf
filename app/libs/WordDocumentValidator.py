from .config import *


class WordDocumentValidator:
    """
    Validator class for Microsoft Word documents.
    Checks table contents from a .docx file - there should be from 1 to 3 tables with specific structure
    """
    def __init__(self, docx_root, eltree_root, namespace):
        self.doc_root = docx_root
        self.eltree_root = eltree_root
        self.ns = namespace
        self.warnings = []
        self.errors = []

    def validate_table_count(self):
        if not len(self.doc_root.tables):
            self.errors.append({"type": "Table Count", "message": "Invalid number of tables"})
            return False
        return True

    def validate_table_column_names(self, table, table_idx, valid_column_names = VALID_COLUMN_NAMES):
        try:
            column_names = []
            for i, row in enumerate(table.iter(f"{self.ns}tr")):
                if i == 0:
                    column_names = [self._get_cell_text(cell, part="first") for cell in row.iter(f"{self.ns}tc")]
                    break
            if column_names != valid_column_names:
                raise ValueError(f"Invalid column names in Table #{table_idx}: {column_names}")
            return True
        except Exception as e:
            self.warnings.append({"type": "Column Names", "message": f"{e}"})
            return False

    # def validate_column_names(self, valid_column_names = VALID_COLUMN_NAMES):
    #     try:
    #         for idx, table in enumerate(self.eltree_root.iter(f"{self.ns}tbl")):
    #             column_names = []
    #             for i, row in enumerate(table.iter(f"{self.ns}tr")):
    #                 if i == 0:
    #                     column_names = [self._get_cell_text(cell, part="first") for cell in row.iter(f"{self.ns}tc")]
    #                     break
    #             if column_names != valid_column_names:
    #                 raise ValueError(f"Invalid column names in Table #{idx}: {column_names}")
    #         return True
    #     except Exception as e:
    #         self.warnings.append({"type": "Column Names", "message": f"{e}"})
    #         return False

    def validate_topic_uniqueness(self):
        try:
            for idx, table in enumerate(self.eltree_root.iter(f"{self.ns}tbl")):
                table_topics = [self._get_cell_text(row.findall(f"{self.ns}tc")[1], part="first") for row in table.iter(f"{self.ns}tr")][1:]
                unique_topics = set()
                dupes = [x for x in table_topics if x in unique_topics or unique_topics.add(x)]
                if dupes:
                    raise ValueError(f"Duplicate topics in Table #{idx}: {', '.join(dupes)}")
            return True
        except Exception as e:
            self.warnings.append({"type": "Topic Uniqueness", "message": f"{e}"})
            return False

    def validate_row_empty(self):
        try:
            for idx, table in enumerate(self.eltree_root.iter(f"{self.ns}tbl")):
                for i, row in enumerate(table.iter(f"{self.ns}tr")):
                    if i:  # [1:0]
                        if all(not self._get_cell_text(cell) for cell in row.iter(f"{self.ns}tc")):
                            raise ValueError(f"Empty row found in a Table #{idx}")
            return True
        except Exception as e:
            self.warnings.append({"type": "Empty Row", "message": f"{e}"})
            return False

    def _get_cell_text(self, cell, part=""):
        texts = [node.text for node in cell.iter(f"{self.ns}t") if node.text]
        if part == "first":
            return texts[0]
        elif part == "second":
            return "".join(texts[1:]) if len(texts)>1 else ""
        else:
            return "".join(texts)

    def validate(self):
        self.validate_table_count()
        # self.validate_column_names()      # table D(3) [No, Document], table F(5) [No, Date, Phase, Short descr of activity]
        # self.validate_topic_uniqueness()  # there are many parameters with the same name
        self.validate_row_empty()
        # return not len(self.errors)

    def get_warnings(self):
        return self.warnings

    def get_errors(self):
        return self.errors