import config
from env import *
from collections import defaultdict
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from svglib.svglib import svg2rlg

BUG_DICT = defaultdict(set)


def draw_logo(path):
    svg_file = open(path)
    drawing = svg2rlg(svg_file)
    # Scale the Drawing.
    scale = 0.25
    drawing.scale(scale, scale)
    drawing.width *= scale
    drawing.height *= scale

    return drawing


def add_logo(doc):
    logo_path = os.path.join(os.path.join(config.ROOT_PATH, "resource"), "logo.svg")
    drawing = draw_logo(logo_path)
    doc.append(Image(drawing, hAlign="CENTER"))
    doc.append(Spacer(1, 50))
    return doc


def add_title(doc):
    doc.append(Spacer(1, 20))
    doc.append(Paragraph("TokenAuditor", ParagraphStyle(name='Name', fontFamily="Arial",
                                                        fontSize=36, alignment=TA_CENTER)))
    doc.append(Spacer(1, 50))
    return doc


def add_metainfo(doc, contract_name, epochs, valid_cnt):
    doc.append(Paragraph("Contract Detected: "+str(contract_name)+".sol"))
    doc.append(Spacer(1, 6))
    doc.append(Paragraph("Running for " + str(epochs) + " epochs"))
    doc.append(Spacer(1, 6))
    doc.append(Paragraph("Generate " + str(valid_cnt)+" valid test cases"))
    doc.append(Spacer(1, 6))
    return doc


def add_risk(doc, bug_collection):
    for bug_item in bug_collection:
        # print(bug_item.method, bug_item.transaction, bug_item.risk)
        doc.append(Paragraph("Risk: "+str(bug_item.risk)))
        if not(bug_item.risk == "Not Token Contract" or bug_item.risk == "Not State Mutation Token Contract"):
            doc.append(Paragraph("Function: " + str(bug_item.transaction["method"])))
            doc.append(Paragraph("Input(s): " + str(bug_item.transaction["f_para"])))
            doc.append(Spacer(1, 6))
    return doc


def res_report(contract_name, bug_collection, tx_epochs, valid_cnt):
    # print(bug_collection)
    document = []
    document = add_logo(document)
    # document = add_title(document)
    document = add_metainfo(document, contract_name, tx_epochs, valid_cnt)
    document = add_risk(document, bug_collection)

    file_path = os.path.join(config.RES_PATH, contract_name + "_report.pdf")
    SimpleDocTemplate(file_path, pagesize=letter, rightMargin=12, leftMargin=12,
                      topMargin=12, bottomMargin=6).build(document)
