import os
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .MongoDBClient import MongoDBClient


pdfmetrics.registerFont(TTFont("DejaVuSans", f"{os.path.dirname(__file__)}/fonts/DejaVuSans.ttf"))

class PdfGenerator:
    """
    Class for PDF document generation from json
    """
    def __init__(self, document_id):
        self.logger = logging.getLogger(__name__)
        self.mongo_client = MongoDBClient()
        self.document_id = document_id
        self.load_data()

        # Default layout settings
        self.page_width, self.page_height = letter
        self.padding = 40
        self.line_height = 20
        self.styles = getSampleStyleSheet()
        self.font_name = "Helvetica"
        self.font_size = 11

    def set_layout(self, page_width, page_height, padding):
        self.page_width = page_width
        self.page_height = page_height
        self.padding = padding

    def set_font(self, font_name, font_size):
        self.font_name = font_name
        self.font_size = font_size

    def load_data(self):
        self.logger.info(f"Fetching document {self.document_id} from DB")
        self.data = self.mongo_client.get_parsed_data_by_id(self.document_id)
        if not self.data:
            msg = f"Document {self.document_id} not found in MongoDB"
            self.logger.error(msg)
            raise ValueError(msg)
        self.logger.info("Data fetched from DB")

    def generate_pdf(self, output_filename):
        self.logger.info("Starting PDF generation process")
        try:
            story = []
            self._add_paragraphs_with_tables_to_pdf(story)
            # self._add_paragraphs_to_pdf(story, self.data["paragraphs"])
            # self._add_tables_to_pdf(story, self.data["content"])

            doc = SimpleDocTemplate(output_filename, pagesize=letter)
            doc.build(story)
            self.logger.info(f"PDF successfully generated: {output_filename}")
        except Exception as e:
            self.logger.exception(f"Error generating PDF: {e}")
            raise

    def _add_paragraphs_with_tables_to_pdf(self, story):
        tables = self.data["content"]
        for paragraph in self.data["paragraphs"]:
            content = ""
            for part in paragraph:
                content_type = part["type"]
                if content_type == "checkbox":
                    checkbox = self._draw_checkbox(checked=part["checked"])
                    # story.append(checkbox)
                    content += checkbox
                elif content_type == "text":
                    content += part["content"]
                    p = Paragraph(content, self.styles["Normal"])
                    story.append(p)
                    content = ""
                elif content_type == "table":
                    try:
                        group = tables.pop(0)
                        table = self._draw_table(group)
                        story.append(table)
                    except Exception as ex:
                        continue
            story.append(Spacer(1, 20))

    def _add_paragraphs_to_pdf(self, story, paragraphs):
        for paragraph in paragraphs:
            content = ""
            for part in paragraph:
                content_type = part["type"]
                if content_type == "checkbox":
                    checkbox = self._draw_checkbox(checked=part["checked"])
                    # story.append(checkbox)
                    content += checkbox
                elif content_type == "text":
                    content += part["content"]
                    p = Paragraph(content, self.styles["Normal"])
                    story.append(p)
                    content = ""
            story.append(Spacer(1, 20))

    def _add_tables_to_pdf(self, story, content):
        for group in content:
            table = self._draw_table(group)
            story.append(table)
            story.append(Spacer(1, 20))

    def _draw_table(self, group):
        groupName = group["groupName"]
        table_data = [list(group["content"][0].keys())]  # Column headers

        for item in group["content"]:
            row = []
            for idx, key in enumerate(table_data[0]):
                cell_content = item.get(key, {})
                if idx == 0:
                    cell_content = ". ".join([cell_content.get("no", ""), cell_content.get("name", "&nbsp")]).strip(". ")
                else:
                    cell_content = self._replace_unicode_in_text(cell_content.get("value", ""))
                p = Paragraph(cell_content, self.styles["Normal"])
                row.append(p)
            table_data.append(row)

        table = Table(table_data, colWidths=self._get_column_widths(table_data))
        self._style_table(table)
        return table

    def _get_column_widths(self, table_data):
        num_cols = len(table_data[0])
        col_width = (self.page_width - 2 * self.padding) / num_cols
        return [col_width] * num_cols  # Equal width for each column

    def _style_table(self, table):
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

    def _draw_checkbox(self, checked=False):
        checkbox_character = "☑" if checked else "☐"  # "[&#x2714;]" if checked else "[&nbsp;&nbsp;]"
        res = f'<font name="DejaVuSans">{checkbox_character}</font>&nbsp;&nbsp;'
        return res

    def _replace_unicode_in_text(self, text):
        items = ["☑", "☐"]
        items_to_replace = {item: f'<font name="DejaVuSans">{item}</font>' for item in items}
        translation_table = str.maketrans(items_to_replace)
        return text.translate(translation_table)
