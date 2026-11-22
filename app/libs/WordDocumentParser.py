import zipfile
from io import StringIO
import re
from docx import Document
import xml.etree.ElementTree as ET
from .DocumentParser import DocumentParser
from .WordDocumentValidator import WordDocumentValidator


class WordDocumentParser(DocumentParser):
    """
    Parser class for Microsoft Word documents.
    Extracts paragraphs and structured table contents from a .docx file.
    """
    def __init__(self, file_path):
        super().__init__(file_path)
        try:
            self.docx = Document(file_path)
            with zipfile.ZipFile(file_path, "r") as docx_zip:
                self.xml_content = docx_zip.read("word/document.xml").decode("utf-8")
                self.xml_tree = ET.ElementTree(ET.fromstring(self.xml_content))
                self.doc_root = self.xml_tree.getroot()
                self.comments_root = None
                self.comments = dict()
                if "word/comments.xml" in docx_zip.namelist():
                    with docx_zip.open("word/comments.xml") as comments_xml:
                        self.comments_xml_content = comments_xml.read().decode("utf-8")
                        self.comments_tree = ET.ElementTree(ET.fromstring(self.comments_xml_content))
                        self.comments_root = self.comments_tree.getroot()
                self._get_namespaces(self.xml_content)
                self._build_parents_map()
                self._parse_comments()
                self.validator = WordDocumentValidator(self.docx, self.doc_root, self.ns)
        except Exception as e:
            self.logger.error(f"Error processing Word document: {e}", exc_info=True)
            # raise ValueError(f"Error processing Word document: {e}")
            raise

    def _get_namespaces(self, xml_content):
        self.namespaces = dict([
            node for _, node in ET.iterparse(
                StringIO(xml_content), events=['start-ns']
            )
        ])
        self.ns = "{"+self.namespaces["w"]+"}"

    def _build_parents_map(self):
        self.xml_tree_parents = {c: p for p in self.doc_root.iter() for c in p}

    def parse(self):
        self.validator.validate()
        self.errors = self.validator.get_errors()
        self.warnings = self.validator.get_warnings()

        if self.errors:
            for error in self.errors:
                self.logger.error(f"Validation warning ({error['type']}): {error['message']}")
            parsed_data = None
        else:
            if self.warnings:
                for warning in self.warnings:
                    self.logger.warning(f"Validation warning ({warning['type']}): {warning['message']}")

            self.logger.info("Document validation passed. Proceeding with parsing.")
            parsed_data = {
                "paragraphs": self._parse_paragraphs(),
                "headings": self._parse_headings(),
                "content": self._parse_groups()
            }
            self.logger.info("Document parsing passed. Proceeding with saving into DB.")
        return parsed_data

    def _parse_paragraphs(self):
        # paragraphs = [p.text for p in self.docx.paragraphs if p.text.strip()]
        paragraphs = []
        table_placeholder_added = False

        for para in self.doc_root.iter(f"{self.ns}p"):
            # Skip paragraphs inside of tables
            if self._is_inside_table(para):
                if not table_placeholder_added:
                    paragraphs.append([{"type": "table", "content": "placeholder"}])
                    table_placeholder_added = True
                continue
            table_placeholder_added = False
            para_text = "".join(node.text for node in para.iter(f"{self.ns}t") if node.text)
            paragraphs.append(self._process_text_string(para_text))

            # checkbox = para.find(".//w14:checkbox", self.namespaces)
            # if checkbox is not None:
            #     checked_elem = checkbox.find(f".//w14:checked", self.namespaces)
            #     is_checked = checked_elem.attrib.get(f"{{{self.namespaces['w14']}}}val") == "1" if checked_elem is not None else False
            #     para_info = {"text": para_text, "checkbox": {"is_checked": is_checked}}
            # else:
            #     para_info = {"text": para_text}

            # paragraphs.append(para_info)

        return paragraphs

    def _is_inside_table(self, element):
        while element is not None:
            if element.tag == f"{self.ns}tbl":
                return True
            element = self.xml_tree_parents.get(element)
        return False

    def _skip_until_end_of_table(self, element):
        depth = 0
        for sibling in element.itersiblings():
            if sibling.tag == f"{self.ns}tbl":
                depth += 1
            if depth == 0:
                break
    def _parse_groups(self):
        groups = []
        for idx, table in enumerate(self.doc_root.iter(f"{self.ns}tbl")):
            table_data = {
                "groupName": f"Group {chr(ord('@')+idx+1)}",  # Group A/B/C
                "content": self._parse_table(table, idx)
            }
            groups.append(table_data)
        return groups

    def _parse_table(self, table, idx):
        if self.validator.validate_table_column_names(table, idx):
            return self._parse_table_products(table)
        else:
            return self._parse_table_non_products(table)

    def _parse_table_products(self, table):
        rows = []
        keys = []

        for i, row in enumerate(table.iter(f"{self.ns}tr")):
            if i == 0:
                keys = [self._get_cell_text(cell, part="first") for cell in row.iter(f"{self.ns}tc")]
            else:
                row_data = {}
                for i, (key, cell) in enumerate(zip(keys, row.iter(f"{self.ns}tc"))):
                    if i == 0:
                        item_number_text = self._get_cell_text(cell)
                        res = re.match("^(\d+\.?\d*\w?)(.*)$", item_number_text)
                        item_number = res[1] if res else ""
                        item_number_notes = res[2] if res else ""
                        item_number_comments = self._get_cell_comments(cell)
                    elif i == 1:
                        row_data["key"] = {
                            "no": item_number,
                            "no_notes": item_number_notes,
                            "name": self._get_cell_text(cell, part="first"),
                            "description": self._get_cell_text(cell, part="second"),
                            "comments": item_number_comments
                        }
                    else:
                        row_data[camel_case_str(key)] = {
                            "value": self._get_cell_text(cell),
                            "history": self._get_cell_history(cell),
                            "comments": self._get_cell_comments(cell)
                        }
                rows.append(row_data)
        return rows

    def _parse_table_non_products(self, table):
        rows = []
        keys = []

        for i, row in enumerate(table.iter(f"{self.ns}tr")):
            if i == 0:
                keys = [self._get_cell_text(cell, part="first") for cell in row.iter(f"{self.ns}tc")]
            else:
                row_data = {}
                rows_num = len(list(row.iter(f"{self.ns}tc")))
                if i == 1 and rows_num > len(keys):
                    # compare len(keys) and len(cells in the row):
                    j = 0
                    new_keys = []
                    while len(new_keys) < rows_num and j < len(keys):
                        split_items = keys[j].split()
                        new_keys.extend(split_items)
                        j += 1
                    keys = new_keys
                for i, (key, cell) in enumerate(zip(keys, row.iter(f"{self.ns}tc"))):
                    row_data[camel_case_str(key)] = {
                        "value": self._get_cell_text(cell),
                        "history": self._get_cell_history(cell),
                        "comments": self._get_cell_comments(cell)
                    }
                rows.append(row_data)
        return rows

    def _get_cell_text(self, cell, part=""):
        texts = [node.text for node in cell.iter(f"{self.ns}t") if node.text]
        if part == "first":
            return texts[0] if len(texts) else ""
        elif part == "second":
            return "".join(texts[1:]) if len(texts)>1 else ""
        else:
            return "".join(texts)

    def _get_cell_history(self, cell):
        cell_history = []

        # Process 'ins' changes
        for change in cell.iter(f"{self.ns}ins"):
            change_details = self._process_change(cell, change, "ins")
            if change_details:
                cell_history.append(change_details)

        # Process 'del' changes
        for change in cell.iter(f"{self.ns}del"):
            change_details = self._process_change(cell, change, "del")
            if change_details:
                cell_history.append(change_details)

        # Sort the history by id
        cell_history.sort(key=lambda x: x["id"]) # datetime
        return cell_history

    def _process_change(self, cell, change, change_type):
        current_change_id = int(change.attrib.get(f"{self.ns}id"))
        current_change_text = "".join(change.itertext()).strip()
        if not current_change_text:
            return None
        old_value = ""
        new_value = ""

        for paragraph in cell.findall(f"{self.ns}p"):
            for child in paragraph:
                child_text = "".join(child.itertext()).strip()
                if child.tag == f"{self.ns}r":
                    old_value += child_text
                    new_value += child_text
                elif child.tag == f"{self.ns}del":
                    old_value += child_text
                    new_value.removesuffix(child_text)
                elif child.tag == f"{self.ns}ins":
                    ins_id = int(child.attrib.get(f"{self.ns}id"))
                    if ins_id <= current_change_id:
                        new_value += child_text
                        if ins_id != current_change_id:
                            old_value += child_text
        step = {
            "id": current_change_id,
            "user": change.attrib.get(f"{self.ns}author"),
            "datetime": change.attrib.get(f"{self.ns}date"),
            "oldValue": old_value,
            "newValue": new_value,
            # "changeType": change_type,
            # "changeValue": current_change_text
        }
        self.logger.debug(f"Parsed change step: {step}")
        return step

    def _get_cell_comments(self, cell):
        comment_ids = self._extract_comment_ids_from_cell(cell)
        return [self.comments[idx] for idx in comment_ids if idx in self.comments]

    def _extract_comment_ids_from_cell(self, cell):
        comment_ids = []
        for comment_start in cell.findall(f".//{self.ns}commentRangeStart"):
            comment_id = comment_start.attrib.get(f"{self.ns}id")
            if comment_id:
                comment_ids.append(comment_id)
        return comment_ids

    def _parse_comments(self):
        if self.comments_root is not None:
            for comment in self.comments_root.findall(f"{self.ns}comment"):
                comment_id = comment.attrib.get(f"{self.ns}id")
                self.comments[comment_id] = {
                        "user": comment.attrib.get(f"{self.ns}author"),
                        "datetime": comment.attrib.get(f"{self.ns}date"),
                        "comment": "".join(comment.itertext()).strip()
                    }
                self.logger.debug(f"Parsed comment: {comment_id}")

    def _parse_headings(self):
        headings = []
        # return headings

        for paragraph in self.doc_root.iter(f"{self.ns}p"):
            # Check if this paragraph is a heading
            pPr = paragraph.find(f"{self.ns}pPr")
            if pPr is not None:
                pStyle = pPr.find(f"{self.ns}pStyle")
                if pStyle is not None and "Heading" in pStyle.get(f"{self.ns}val", ""):
                    # Extract the heading text
                    text = "".join(node.text for node in paragraph.iter(f"{self.ns}t") if node.text)
                    headings.append(text)
        return headings

def camel_case_str(str):
    output = "".join(x for x in str.title() if x.isalnum())
    return output[0].lower() + output[1:]