"""Generate a PDF with ambiguous content that should trigger Human Review."""
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


def create_ambiguous_pdf():
    filepath = os.path.join(output_dir, "corporate_wellness_initiative.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    # Page 1 - Ambiguous: mentions "athlete" and "fitness" once each in a corporate context
    # Should trigger Sports rule (2 matches = 0.60 confidence) then LLM should be uncertain
    # because the context is corporate wellness, not actual sports
    story.append(Paragraph("Corporate Wellness & Employee Engagement Initiative", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Program Overview", heading_style))
    story.append(Paragraph(
        "TechCorp Inc. launched its annual employee wellness initiative in Q3 2024. "
        "The program encourages employees to adopt healthier lifestyles through various "
        "activities organized by the HR department. Employees are encouraged to think like "
        "an athlete when setting personal goals for the quarter. The company hired a "
        "part-time coach to lead group sessions and allocated a modest budget for "
        "fitness memberships and ergonomic desk assessments.",
        body_style
    ))

    story.append(Paragraph("Key Activities", heading_style))
    story.append(Paragraph(
        "1. Weekly step challenges tracked via mobile app<br/>"
        "2. Subsidized gym memberships at partner locations<br/>"
        "3. Monthly nutrition workshops led by external consultants<br/>"
        "4. Ergonomic workspace evaluations for all departments<br/>"
        "5. Annual company picnic with recreational volleyball and relay races",
        body_style
    ))

    story.append(Paragraph("Employee Feedback", heading_style))
    story.append(Paragraph(
        "A survey conducted across 450 employees showed 72% satisfaction with the new "
        "wellness program. Several employees noted that the step challenges helped them "
        "build consistent exercise habits. The HR team plans to expand the program next "
        "year with additional mental health resources and stress management workshops. "
        "Department managers were asked to support flexible scheduling so employees "
        "could participate in lunchtime walking groups.",
        body_style
    ))

    story.append(Spacer(1, 20))

    # Page 2 - Ambiguous: mentions "prescription" once in a corporate benefits context
    # Should trigger Medical rule (1 match = 0.50) then LLM uncertain because it's
    # about employee benefits, not actual medical content
    story.append(Paragraph("Employee Benefits Review - Health Coverage Update", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Benefits Enrollment Summary", heading_style))
    story.append(Paragraph(
        "During the open enrollment period, 89% of eligible employees updated their "
        "benefits selections. The company negotiated new rates with three insurance "
        "providers to offer more competitive premiums. The updated plan includes "
        "expanded prescription drug coverage under Tier 2 for generic alternatives. "
        "Employees in the California and New York offices will see changes to their "
        "provider networks starting January 2025.",
        body_style
    ))

    story.append(Paragraph("Cost Analysis", heading_style))
    story.append(Paragraph(
        "The total employer contribution to employee benefits increased by 4.2% "
        "year-over-year, driven primarily by rising premiums in the northeast region. "
        "The HR and procurement teams evaluated switching to a high-deductible plan "
        "model but decided to maintain the current PPO structure after consulting with "
        "the pharmacy benefits manager. The company will absorb the additional costs "
        "rather than pass them to employees through higher payroll deductions.",
        body_style
    ))

    story.append(Paragraph("Vendor Negotiations", heading_style))
    story.append(Paragraph(
        "Procurement completed negotiations with United Benefits Corp and HealthFirst "
        "Alliance for the 2025 plan year. Key improvements include: lower out-of-pocket "
        "maximums for in-network services, expanded telehealth coverage, and new "
        "partnerships with regional urgent care facilities. The contract terms run for "
        "three years with annual rate adjustment caps of 5%.",
        body_style
    ))

    story.append(Spacer(1, 20))

    # Page 3 - Ambiguous: mentions "revenue" once in a tech product context
    # Should trigger Finance rule (1 match = 0.50) then LLM uncertain because
    # it's a product launch report, not a financial document
    story.append(Paragraph("Q3 Product Launch Performance Report", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Launch Summary", heading_style))
    story.append(Paragraph(
        "The CloudSync Pro platform launched on August 15th with 2,400 enterprise "
        "trial signups in the first two weeks, exceeding the target of 1,800. The "
        "product team attributes the strong adoption to the simplified onboarding "
        "flow and the integration marketplace featuring 45 pre-built connectors. "
        "Early revenue from converted trials reached $340K against a Q3 target of $500K, "
        "with the sales pipeline showing strong momentum heading into Q4.",
        body_style
    ))

    story.append(Paragraph("Customer Segments", heading_style))
    story.append(Paragraph(
        "Mid-market companies (200-2000 employees) represented 62% of trial signups, "
        "while enterprise accounts (2000+ employees) made up 23%. The remaining 15% "
        "were small businesses exploring the platform's free tier. The customer success "
        "team onboarded 18 enterprise accounts with dedicated implementation support. "
        "Geographic distribution was heavily weighted toward North America (71%), "
        "followed by Europe (19%) and Asia-Pacific (10%).",
        body_style
    ))

    story.append(Paragraph("Technical Performance", heading_style))
    story.append(Paragraph(
        "Platform uptime averaged 99.97% during the launch period with two minor "
        "incidents resolved within 15 minutes each. API response times averaged 120ms "
        "at the 95th percentile, well within the 200ms SLA target. The engineering "
        "team deployed 14 hotfix releases addressing customer-reported issues, "
        "primarily related to SSO configuration and data import edge cases. "
        "Infrastructure costs came in 12% under projection due to efficient "
        "auto-scaling implementation.",
        body_style
    ))

    doc.build(story)
    print(f"Created: {filepath}")
    return filepath


if __name__ == "__main__":
    create_ambiguous_pdf()
