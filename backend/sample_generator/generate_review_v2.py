"""Generate a PDF where LLM will say 'maybe relevant' with low confidence,
triggering the human review queue."""
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
    filepath = os.path.join(output_dir, "mixed_context_memo.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    # Page 1: An internal company memo that briefly mentions a medical policy update
    # Only 1 medical keyword ("prescription") in a mostly HR/policy context
    # Rule: 1 match = 0.50 confidence -> LLM called
    # LLM should say "somewhat relevant" with ~0.40 confidence (it IS about prescriptions
    # but in an employee benefits context, not a medical document)
    # Combined: (0.50 * 0.3) + (0.40 * 0.7) = 0.15 + 0.28 = 0.43 < 0.50 -> REVIEW
    story.append(Paragraph("Internal Memo: Q4 Policy Updates for All Departments", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("To: All Department Heads", heading_style))
    story.append(Paragraph(
        "This memo outlines several policy changes taking effect in Q4 2024. Please "
        "distribute to your teams by end of week.",
        body_style
    ))

    story.append(Paragraph("1. Remote Work Policy", heading_style))
    story.append(Paragraph(
        "Effective October 1st, all employees may work remotely up to 3 days per week. "
        "Managers must approve schedules by September 20th. VPN access will be mandatory "
        "for all remote sessions. IT will distribute updated access credentials by Sept 25th.",
        body_style
    ))

    story.append(Paragraph("2. Updated Benefits - Prescription Coverage", heading_style))
    story.append(Paragraph(
        "Our prescription drug plan has been updated for Q4. Employees should note that "
        "generic medication alternatives will now be covered at 100% under Tier 1. Brand-name "
        "options remain at 80% coverage. Please update your pharmacy preferences through "
        "the HR portal by October 15th. Questions should be directed to benefits@techcorp.com.",
        body_style
    ))

    story.append(Paragraph("3. Office Renovation Schedule", heading_style))
    story.append(Paragraph(
        "The 3rd floor renovation will begin November 1st and run through December 15th. "
        "Teams on the 3rd floor will be temporarily relocated to the 5th floor conference "
        "rooms. Please pack personal items by October 28th. Facilities will provide "
        "moving boxes and labels.",
        body_style
    ))

    story.append(Paragraph("4. Year-End Performance Reviews", heading_style))
    story.append(Paragraph(
        "Performance review cycles begin December 1st. All managers must complete "
        "preliminary assessments by December 10th. Self-evaluations are due November 25th. "
        "The new competency framework will be used for the first time this cycle. "
        "HR will hold training sessions for managers on November 5th and 12th.",
        body_style
    ))

    story.append(Spacer(1, 20))

    # Page 2: A tech company blog post that mentions "marathon" in a coding context
    # Only 1 sports keyword ("marathon") but used metaphorically
    # Rule: 1 match = 0.50 -> LLM called
    # LLM should say "maybe relevant" with low confidence since "marathon" is used
    # in a tech hackathon context
    story.append(Paragraph("TechCorp Engineering Blog: Our 48-Hour Hackathon Marathon", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("The Challenge", heading_style))
    story.append(Paragraph(
        "Last weekend, 80 engineers participated in our annual coding marathon "
        "event. Teams of four competed to build innovative prototypes addressing "
        "real customer pain points. The marathon kicked off Friday at 6 PM and "
        "concluded Sunday at 6 PM with final presentations to the executive team.",
        body_style
    ))

    story.append(Paragraph("Winning Projects", heading_style))
    story.append(Paragraph(
        "First place went to Team Phoenix with their AI-powered log analysis tool "
        "that reduced incident response time by 40% in simulated tests. Second place "
        "was awarded to Team Nebula for their automated accessibility testing framework. "
        "Third place went to Team Cascade for a real-time collaboration whiteboard "
        "with integrated code execution.",
        body_style
    ))

    story.append(Paragraph("What We Learned", heading_style))
    story.append(Paragraph(
        "The coding marathon revealed several insights about our engineering culture. "
        "Cross-team collaboration produced better results than siloed efforts. "
        "The most successful teams spent 30% of their time on planning before writing "
        "any code. We plan to incorporate two hackathon events per year going forward. "
        "Several marathon projects have been greenlit for production development in Q1 2025.",
        body_style
    ))

    doc.build(story)
    print(f"Created: {filepath}")
    return filepath


if __name__ == "__main__":
    create_pdf()
