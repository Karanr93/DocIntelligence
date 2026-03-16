"""Generate a PDF that should trigger the Human Review queue.
Content has medical/finance terms used metaphorically or in edge-case contexts."""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

output_dir = os.path.join(os.path.dirname(__file__), "..", "sample_pdfs")
os.makedirs(output_dir, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=20)
heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=13, spaceAfter=10)
body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=8)


def create_pdf():
    filepath = os.path.join(output_dir, "veterinary_clinic_operations.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    # Page 1: Veterinary clinic - uses medical terms but for animals, not humans
    # Keywords: patient, diagnosis, treatment, prescription, therapy, clinical, surgical
    # LLM should be uncertain: is veterinary medicine "Medical" category?
    story.append(Paragraph("Paws & Claws Veterinary Clinic - Quarterly Report Q3 2024", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Patient Intake Summary", heading_style))
    story.append(Paragraph(
        "During Q3 2024, our veterinary clinic admitted 342 animal patients across all "
        "departments. The diagnosis rate improved by 18% following the installation of "
        "our new digital radiography system. Common treatment protocols included dental "
        "cleanings (87 cases), vaccination updates (124 cases), and orthopedic consultations "
        "(43 cases). Our clinical laboratory processed 1,200 blood panels with an average "
        "turnaround time of 4 hours. The surgical suite performed 56 procedures including "
        "12 emergency operations. Each patient receives a customized therapy plan developed "
        "by our team of licensed veterinarians.",
        body_style
    ))

    story.append(Paragraph("Prescription & Pharmacy Operations", heading_style))
    story.append(Paragraph(
        "The in-house pharmacy filled 890 prescriptions during the quarter. The most "
        "commonly prescribed medication categories were antibiotics (34%), anti-inflammatory "
        "drugs (22%), and heartworm preventatives (19%). We implemented a new chronic "
        "condition management program for diabetic pets, which has enrolled 28 patients "
        "in ongoing monitoring protocols. The pharmacy team conducted medication "
        "reconciliation reviews for all surgical patients to prevent adverse drug "
        "interactions. Our healthcare approach emphasizes preventive care and early "
        "intervention to reduce the need for acute emergency treatment.",
        body_style
    ))

    story.append(Spacer(1, 20))

    # Page 2: Fantasy sports platform financials - uses finance AND sports terms
    # but it's a tech/gaming platform, not traditional finance or sports
    story.append(Paragraph("DraftKing Analytics - Platform Performance & Revenue Report", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Platform Revenue Analysis", heading_style))
    story.append(Paragraph(
        "The fantasy sports platform generated $4.7 million in revenue during Q3, "
        "driven by the NFL and NBA season openers. Player engagement metrics showed "
        "2.1 million active users placing entries across 14 sports categories. "
        "The cash flow from tournament entry fees exceeded projections by 15%, while "
        "the portfolio of promotional offerings was optimized to reduce customer "
        "acquisition costs. Revenue per user increased to $2.24 from $1.89 in Q2.",
        body_style
    ))

    story.append(Paragraph("Competitive Landscape & Financial Outlook", heading_style))
    story.append(Paragraph(
        "Market analysis indicates growing competition from three new entrants in the "
        "daily fantasy sports space. Our financial audit for Q3 confirmed regulatory "
        "compliance across all 38 operating states. The balance sheet reflects $12M "
        "in reserved prize pool obligations. Coach-mode, a new feature allowing users "
        "to simulate lineup strategies, drove a 23% increase in session duration. "
        "The stadium partnership program expanded to 8 venues offering in-seat "
        "fantasy sports experiences during live games.",
        body_style
    ))

    doc.build(story)
    print(f"Created: {filepath}")
    return filepath


if __name__ == "__main__":
    create_pdf()
