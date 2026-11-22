import unittest
import os
from unittest.mock import patch, MagicMock
from app.libs.PdfGenerator import PdfGenerator


class TestPdfGenerator(unittest.TestCase):

    def setUp(self):
        self.output_doc_path = "data/sample_word.pdf"
        self.mongo_patch = patch("app.libs.PdfGenerator.MongoDBClient")
        self.mock_mongo = self.mongo_patch.start()
        self.mock_mongo.return_value.get_parsed_data_by_id.return_value = MOCK_SOURCE_JSON
        self.generator = PdfGenerator("document_id")

    def tearDown(self):
        self.mongo_patch.stop()

    def test_load_data(self):
        self.generator.load_data()
        self.assertEqual(self.generator.data, MOCK_SOURCE_JSON)

    def test_load_data_failure(self):
        self.mock_mongo.return_value.get_parsed_data_by_id.return_value = None
        with self.assertRaises(ValueError):
            self.generator.load_data()

    def test_generate_pdf(self):
        self.generator.generate_pdf(self.output_doc_path)
        self.assertTrue(os.path.isfile(self.output_doc_path))
        os.remove(self.output_doc_path)

    def test_add_paragraphs_with_tables_to_pdf(self):
        story = []
        self.generator._add_paragraphs_with_tables_to_pdf(story)
        self.assertEqual(len(story), 14)  # Spacer after each paragraph

    def test_add_paragraphs_to_pdf(self):
        story = []
        self.generator._add_paragraphs_to_pdf(story, MOCK_SOURCE_JSON["paragraphs"])
        self.assertEqual(len(story), 13)

    # def test_add_tables_to_pdf(self):
    #     story = []
    #     self.generator._add_tables_to_pdf(story, MOCK_SOURCE_JSON["content"])
    #     self.assertEqual(len(story), 2)  # Spacer after each table

    def test_draw_checkbox(self):
        checkbox = self.generator._draw_checkbox(checked=True)
        self.assertEqual(checkbox, '<font name="DejaVuSans">☑</font>&nbsp;&nbsp;')
        checkbox = self.generator._draw_checkbox(checked=False)
        self.assertEqual(checkbox, '<font name="DejaVuSans">☐</font>&nbsp;&nbsp;')



MOCK_SOURCE_JSON = {
    "paragraphs": [
        [
            {
                "type": "text",
                "content": "Scope/ Goal of SOP Data tracking of regulatory procedures between GRA & LRA/RA-Hub and all concerned departments & functions"
            }
        ],
        [
            {
                "type": "text",
                "content": "TO BE FILLED IN:"
            }
        ],
        [
            {
                "type": "checkbox",
                "checked": False
            },
            {
                "type": "text",
                "content": "New Marketing Authorization"
            }
        ],
        [
            {
                "type": "checkbox",
                "checked": True
            },
            {
                "type": "text",
                "content": "Variations/Notifications/Other not affecting the product information"
            }
        ],
        [
            {
                "type": "text",
                "content": "3 A) Basic Information"
            }
        ],
        [
            {
                "type": "table",
                "content": "placeholder"
            }
        ],
        [
            {
                "type": "text",
                "content": ""
            }
        ]
    ],
    # "headings": [
    #     "Scope/ Goal of SOP \u201cData tracking of regulatory procedures between GRA & LRA/RA-Hub and all concerned departments & functions\u201c- HC-DDDD-D-5-2-05-002940:"
    # ],
    "content": [
        {
            "groupName": "Group A",
            "content": [
                {
                    "key": {
                        "no": "1",
                        "no_notes": "#",
                        "name": "Is an \u201cOld\u201d commitment fulfilled ",
                        "description": "<Yes or No>If yes please provide <commitment identifier> (as defined by/ received from Datamanagement).Please additionally indicate <If an approval of commitment by Health Authority is expected or not>. Depending on that information the commitment can be closed in the RA database.",
                        "comments": [
                            {
                                "user": "Xiao Chen",
                                "datetime": "2024-01-04T11:11:00Z",
                                "comment": "can be requested from GRA Datamanagement as database excerpt"
                            }
                        ]
                    },
                    "atDispatch": {
                        "value": "No",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "2",
                        "no_notes": "",
                        "name": "Is a \u201cNew\u201d commitment given",
                        "description": "<Yes or No>If yes then add exact date in format <dd.mm.yyyy>. If a commitment is given already before the RA procedure is started, give the date of dispatch and / or submission in the respective column \u201cAt Dispatch\u201d/ \u201cAt Submission\u201d.  In case the commitment is given during the ongoing RA procedure include the dispatch and / or submission date under the column \u201cAt Outcome\u201d.In addition please complete the next lines.",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "No",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "3",
                        "no_notes": "",
                        "name": "Description of the commitment",
                        "description": " Please add a <short description> as applicable.",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "4",
                        "no_notes": "",
                        "name": "Type of Commitment",
                        "description": "<Please tick as applicable.> ",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "\u2610 Commitment to be fulfilled only once with specific timelines\u2610 Commitment to be fulfilled only once without specific timelines\u2610 Commitment (potentially) be fulfilled more than once",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "\u2610 Commitment to be fulfilled only once with specific timelines\u2610 Commitment to be fulfilled only once without specific timelines\u2610 Commitment (potentially) be fulfilled more than once",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "\u2610 Commitment to be fulfilled only once with specific timelines\u2610 Commitment to be fulfilled only once without specific timelines\u2610 Commitment (potentially) be fulfilled more than once",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "5",
                        "no_notes": "",
                        "name": "Is ",
                        "description": "an approval of commitment by Health Authority expected?<Yes or No>",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "No",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "6",
                        "no_notes": "",
                        "name": "Commitment related to",
                        "description": "<Please tick as applicable.> ",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "\u2610 Safety\u2610 Quality\u2610 Safety + Quality\u2610 Other",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "\u2610 Safety\u2610 Quality\u2610 Safety + Quality\u2610 Other",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "\u2610 Safety\u2610 Quality\u2610 Safety + Quality\u2610 Other",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "7",
                        "no_notes": "",
                        "name": "Market presentations (containers) in scope",
                        "description": "<Please tick all if applicable.> If not all are applicable, please specify <the concerned container types, fill volume(s) and pack size(s)>.",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "\u2610 All\u2610 Limited, namely:",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "\u2610 All\u2610 Limited, namely:",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "\u2610 All\u2610 Limited, namely:",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "8",
                        "no_notes": "",
                        "name": "Desired notification date for upcoming planned submission",
                        "description": "Please indicate exact date<dd.mm.yyyy>.",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "",
                        "history": [],
                        "comments": []
                    }
                },
                {
                    "key": {
                        "no": "9",
                        "no_notes": "",
                        "name": "Planned submission date to H",
                        "description": "ealth AuthorityPlease indicate exact date<dd.mm.yyyy>.",
                        "comments": []
                    },
                    "atDispatch": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atSubmission": {
                        "value": "",
                        "history": [],
                        "comments": []
                    },
                    "atOutcome": {
                        "value": "",
                        "history": [],
                        "comments": []
                    }
                }
            ]
        }
    ]
}