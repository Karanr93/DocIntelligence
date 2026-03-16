"""Generate a PDF with genuinely borderline content that should trigger Human Review."""
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


def create_borderline_pdf():
    filepath = os.path.join(output_dir, "sports_medicine_clinic_report.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    # Page 1 - Sports Medicine: genuinely both Medical AND Sports
    # Has medical keywords (patient, diagnosis, therapy, surgical) AND sports keywords (athlete, fitness, coach)
    # LLM should be uncertain about primary category
    story.append(Paragraph("City Sports Medicine Clinic - Annual Operations Report", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Patient Demographics & Referral Patterns", heading_style))
    story.append(Paragraph(
        "The City Sports Medicine Clinic treated 1,847 patients during the 2024 fiscal year, "
        "representing a 12% increase over the prior year. The majority of referrals came from "
        "local sports organizations and high school athletic programs. Each athlete undergoes "
        "a comprehensive diagnosis assessment before any treatment plan is developed. "
        "Our physician team includes three board-certified specialists in orthopedic surgery "
        "and two physical therapy directors who work closely with each coach to develop "
        "return-to-play protocols. The clinic's fitness evaluation lab was upgraded with "
        "new VO2 max testing equipment in March.",
        body_style
    ))

    story.append(Paragraph("Common Conditions Treated", heading_style))
    story.append(Paragraph(
        "ACL reconstruction remained the most common surgical procedure, accounting for "
        "23% of all operations. Chronic tendinopathy cases increased significantly among "
        "recreational marathon runners. Our clinical team observed a 15% rise in "
        "concussion evaluations, primarily from football and soccer player referrals. "
        "The prescription rate for anti-inflammatory medication decreased by 8% as more "
        "patients opted for physical therapy-based recovery programs. "
        "Post-surgical rehabilitation outcomes improved with the new aquatic therapy pool.",
        body_style
    ))

    story.append(Spacer(1, 20))

    # Page 2 - Financial aspects of a sports organization: both Finance AND Sports
    story.append(Paragraph("Regional Youth Sports Foundation - Financial Sustainability Review", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Revenue & Funding Sources", heading_style))
    story.append(Paragraph(
        "The Foundation's total revenue for FY2024 was $2.3 million, derived from "
        "tournament registration fees (41%), corporate sponsorship (28%), municipal grants "
        "21%), and individual donations (10%). The basketball and soccer programs generated "
        "the highest registration revenue, while the swimming and tennis programs required "
        "subsidization from general funds. The portfolio of invested endowment funds "
        "returned 7.2% net of fees, slightly below the benchmark.",
        body_style
    ))

    story.append(Paragraph("Operational Expenses", heading_style))
    story.append(Paragraph(
        "Total operating expenses reached $2.1 million. Stadium and facility maintenance "
        "represented the largest expense category at 34%, followed by coach and referee "
        "compensation at 29%. The Foundation's cash flow remained positive throughout "
        "the year despite unexpected capital expenditures for field renovation. "
        "The fiscal year ended with a modest surplus of $180K, which the board allocated "
        "to the facility improvement reserve fund. An independent financial audit "
        "confirmed compliance with all grant reporting requirements.",
        body_style
    ))

    story.append(Spacer(1, 20))

    # Page 3 - Healthcare worker injury from sports: Medical context with sports mentions
    story.append(Paragraph("Workplace Injury Report - Memorial Hospital Staff", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Incident Summary", heading_style))
    story.append(Paragraph(
        "Three hospital staff members sustained injuries during the annual hospital "
        "charity marathon event held on September 14th. The hospital's occupational "
        "health physician assessed each patient and recommended appropriate treatment. "
        "One nurse required prescription pain medication following a stress fracture "
        "sustained during the marathon. The clinical assessment indicated the injury was "
        "consistent with inadequate training preparation. The therapy protocol includes "
        "six weeks of progressive weight-bearing exercises.",
        body_style
    ))

    story.append(Paragraph("Workers Compensation Analysis", heading_style))
    story.append(Paragraph(
        "The hospital's insurance provider reviewed the three claims totaling $14,200. "
        "The claims were initially disputed as the injuries occurred during a voluntary "
        "recreational event rather than standard clinical duties. After review by the "
        "healthcare risk management team, two claims were approved under the employer- "
        "sponsored wellness program coverage. The third claim involving chronic knee "
        "pain from the marathon remains under medical review. The pharmacy benefits "
        "coordinator confirmed coverage for prescribed medications under the hospital's "
        "self-insured plan.",
        body_style
    ))

    doc.build(story)
    print(f"Created: {filepath}")
    return filepath


if __name__ == "__main__":
    create_borderline_pdf()
