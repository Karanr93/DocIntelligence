"""Generate 10 synthetic sample PDFs with realistic Medical, Finance, and Sports clause content."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_pdfs")

DOCUMENTS = [
    {
        "filename": "healthcare_policy_2024.pdf",
        "pages": [
            {"type": "Medical", "content": """
<b>Healthcare Coverage Policy - Section 4.2: Medical Benefits</b><br/><br/>
This policy provides comprehensive medical coverage for all enrolled members. The patient is entitled to
preventive care services including annual physical examinations, diagnostic screening, and immunizations
at no additional copay. Treatment for chronic conditions such as diabetes, hypertension, and cardiovascular
disease is covered under the standard plan with a $25 copay per physician visit.<br/><br/>
<b>Prescription Medication Coverage:</b> Generic medications are covered at 80% after the $500 annual
deductible is met. Brand-name medications require prior authorization from the attending physician.
The maximum out-of-pocket expense for prescription drugs shall not exceed $3,000 per calendar year.<br/><br/>
<b>Surgical Procedures:</b> All medically necessary surgical procedures require pre-certification.
Emergency surgical interventions are covered at 90% of the contracted rate. Post-surgical rehabilitation
and physical therapy sessions are limited to 30 visits per condition per year.<br/><br/>
Hospital admission requires a pre-existing condition review. The clinical team must submit documentation
including diagnosis codes, treatment plans, and expected duration of stay. Mental health services including
therapy and psychiatric consultation are covered with parity to physical health benefits.
"""},
            {"type": "Finance", "content": """
<b>Financial Terms and Premium Structure</b><br/><br/>
The annual premium for individual coverage is $4,800, payable in monthly installments of $400.
Family coverage is available at $12,000 per year ($1,000 monthly). The employer contribution
covers 70% of the premium cost, with the remaining 30% deducted from employee payroll.<br/><br/>
<b>Investment of Premium Reserves:</b> Premium reserves are invested in a diversified portfolio
consisting of 60% fixed-income securities, 25% equity funds, and 15% money market instruments.
The expected annual return on the investment portfolio is 5.2%, with quarterly dividend distributions
to the reserve fund. The fiscal year budget allocation for claims processing is $2.4 million.<br/><br/>
Revenue from policyholder premiums totaled $48.5 million in the previous fiscal year, representing
a 12% increase over the prior period. Operating expenses including administrative costs, claims
adjudication, and regulatory compliance totaled $38.2 million, yielding a net operating profit of
$10.3 million. The balance sheet reflects total assets of $125 million with a debt-to-equity ratio of 0.35.
"""},
            {"type": "Medical", "content": """
<b>Clinical Guidelines for Treatment Authorization</b><br/><br/>
All treatment requests must be evaluated against evidence-based clinical guidelines. The healthcare
provider must document the patient's medical history, current symptoms, and proposed treatment plan.
Diagnostic imaging including MRI, CT scans, and X-rays requires referral from the primary care physician.<br/><br/>
Laboratory tests including complete blood count (CBC), metabolic panels, and specialized biomarker
assays are covered when ordered by a licensed physician. Preventive screening for cancer, including
mammography, colonoscopy, and PSA testing, follows the recommended schedule based on age and risk factors.<br/><br/>
Chronic disease management programs are available for patients diagnosed with diabetes mellitus,
congestive heart failure, chronic obstructive pulmonary disease (COPD), and asthma. Each patient
receives a personalized care plan developed by a multidisciplinary clinical team including physicians,
nurses, pharmacists, and social workers.
"""}
        ]
    },
    {
        "filename": "sports_league_contract.pdf",
        "pages": [
            {"type": "Sports", "content": """
<b>Professional Sports League - Player Contract Agreement</b><br/><br/>
This contract is entered between the Player (hereinafter "Athlete") and the Team for participation
in the 2024-2025 championship season. The athlete agrees to participate in all scheduled training
sessions, regular season matches, and tournament competitions as directed by the head coach.<br/><br/>
<b>Compensation:</b> The player shall receive a base salary of $2.5 million per season, with
performance bonuses of up to $500,000 based on team standings, individual statistics, and playoff
advancement. Endorsement and sponsorship revenues are subject to a 15% commission to the league.<br/><br/>
The team retains the right of first refusal for contract extensions and player transfers. Any trade
or transfer to another team requires mutual consent and compliance with league draft regulations.
The player must maintain fitness standards as evaluated by the team's medical and coaching staff
during pre-season and mid-season assessments. Stadium attendance bonuses apply when home game
attendance exceeds 40,000 spectators.
"""},
            {"type": "Medical", "content": """
<b>Player Health and Medical Provisions</b><br/><br/>
The team shall provide comprehensive medical coverage for all sports-related injuries sustained
during training, competition, or team-sanctioned activities. Each player must undergo a pre-season
physical examination including cardiovascular screening, musculoskeletal assessment, and concussion
baseline testing conducted by licensed team physicians.<br/><br/>
Injury rehabilitation and physical therapy services are provided at the team's medical facility.
Players diagnosed with concussions must follow the league's return-to-play protocol, which requires
clearance from an independent neurologist. Prescription medications for injury management are covered
at 100% with no deductible. Surgical procedures resulting from sports injuries are fully covered
including post-operative rehabilitation. The team physician must maintain detailed medical records
and treatment histories for each athlete.
"""},
            {"type": "Finance", "content": """
<b>Financial Obligations and Revenue Sharing</b><br/><br/>
The league operates under a revenue-sharing model where broadcast rights, merchandise sales, and
ticket revenue are distributed among participating teams. Each team receives a base allocation of
$15 million from the central fund, plus performance-based distributions tied to season rankings.<br/><br/>
Player salary obligations are capped at 48% of team revenue under the league's salary cap provisions.
Teams exceeding the luxury tax threshold of $140 million in total payroll are subject to a progressive
penalty tax. Investment in stadium infrastructure and training facilities is eligible for league
co-financing at favorable interest rates. The annual audit of team finances must be conducted by
an independent accounting firm and submitted to the league office by March 31 of each year.
"""}
        ]
    },
    {
        "filename": "investment_portfolio_report.pdf",
        "pages": [
            {"type": "Finance", "content": """
<b>Q4 2024 Investment Portfolio Performance Report</b><br/><br/>
The diversified investment portfolio achieved a total return of 8.7% for the fiscal year ending
December 31, 2024. Equity holdings generated a 12.3% return, outperforming the benchmark index
by 180 basis points. Fixed-income securities returned 4.1%, reflecting the rising interest rate
environment and strategic duration management.<br/><br/>
<b>Asset Allocation:</b> Total portfolio value stands at $285 million, allocated as follows:
U.S. equities (35%), international equities (15%), investment-grade bonds (25%), high-yield bonds
(10%), real estate investment trusts (8%), and cash equivalents (7%). Portfolio rebalancing was
executed in September to reduce equity exposure by 5% in anticipation of market volatility.<br/><br/>
<b>Revenue Analysis:</b> Dividend income totaled $8.4 million, capital gains realized were $12.1 million,
and interest income from fixed-income holdings was $6.8 million. Management fees and transaction
costs totaled $1.2 million, resulting in net investment income of $26.1 million. The budget
for the upcoming fiscal year projects a 6-8% target return with moderate risk tolerance.
"""},
            {"type": "Finance", "content": """
<b>Risk Assessment and Compliance</b><br/><br/>
The portfolio maintains a Value-at-Risk (VaR) of 2.3% at the 95% confidence level, within the
acceptable threshold of 3.0%. Credit exposure to any single issuer does not exceed 5% of total
assets. The Sharpe ratio for the overall portfolio is 1.45, indicating favorable risk-adjusted returns.<br/><br/>
Tax optimization strategies employed during the fiscal year include tax-loss harvesting on
underperforming equity positions, generating $3.2 million in capital loss offsets. Municipal bond
holdings of $18 million provide tax-exempt interest income. All investment activities comply with
regulatory requirements including SEC reporting obligations, fiduciary duty standards, and
anti-money laundering (AML) provisions. The loan portfolio maintains a default rate below 0.5%,
with mortgage-backed securities accounting for 12% of fixed-income holdings.
"""},
            {"type": "Sports", "content": """
<b>Sports and Entertainment Investment Holdings</b><br/><br/>
The portfolio includes strategic investments in the sports and entertainment sector. A $15 million
equity stake in a professional basketball franchise represents a 3% minority ownership position.
The team's valuation has appreciated 22% over the past three years, driven by new broadcasting
rights and increased stadium revenue from championship season performances.<br/><br/>
Additional sports-related investments include a $5 million position in a sports technology company
developing athlete performance analytics, and a $3 million investment in a fitness equipment
manufacturer. The sports entertainment sector allocation is projected to generate a 15% annual
return based on league expansion, increased viewership, and growing endorsement markets. Player
transfer fees in European football leagues have created new investment opportunities in player
development academies and talent scouting operations.
"""}
        ]
    },
    {
        "filename": "hospital_operations_manual.pdf",
        "pages": [
            {"type": "Medical", "content": """
<b>Hospital Operations Manual - Chapter 7: Patient Care Standards</b><br/><br/>
All clinical staff must adhere to evidence-based patient care protocols established by the hospital's
medical board. Physician orders must be documented in the electronic health record (EHR) system within
2 hours of the patient encounter. Nursing staff are required to perform patient assessments every
4 hours for general ward patients and every 1 hour for intensive care unit (ICU) patients.<br/><br/>
<b>Emergency Department Protocols:</b> Patients presenting to the emergency department are triaged
using the Emergency Severity Index (ESI) system. Level 1 (critical) patients receive immediate
attention. All trauma cases require activation of the surgical team within 15 minutes. Diagnostic
imaging and laboratory results for emergency patients must be prioritized with a 30-minute turnaround.<br/><br/>
Infection control measures include mandatory hand hygiene compliance, isolation protocols for
communicable diseases, and antibiotic stewardship programs. All healthcare workers must complete
annual training on bloodborne pathogen exposure prevention and proper use of personal protective equipment.
"""},
            {"type": "Medical", "content": """
<b>Pharmacy and Medication Management</b><br/><br/>
The hospital pharmacy operates 24/7 to ensure medication availability for all patient care needs.
Prescription orders are verified by licensed pharmacists before dispensing. High-alert medications
including insulin, anticoagulants, and opioids require double-verification by two independent clinicians.<br/><br/>
Medication administration follows the "five rights" protocol: right patient, right drug, right dose,
right route, and right time. Adverse drug reactions must be reported through the hospital's incident
reporting system within 24 hours. The formulary committee reviews and updates the approved medication
list quarterly based on clinical efficacy, safety profiles, and cost-effectiveness analyses.<br/><br/>
Controlled substance management follows DEA regulations with electronic prescribing for all Schedule
II-V medications. Automated dispensing cabinets are deployed in each nursing unit with biometric
access controls. Annual medication use evaluations are conducted for high-risk drug categories.
"""},
            {"type": "Finance", "content": """
<b>Hospital Financial Operations</b><br/><br/>
The hospital's annual operating budget is $450 million, with revenue primarily derived from patient
services (75%), research grants (12%), and philanthropic contributions (8%). Medicare and Medicaid
reimbursements account for 55% of patient service revenue, with commercial insurance comprising
35% and self-pay patients representing 10%.<br/><br/>
Capital expenditure for the current fiscal year totals $35 million, allocated to medical equipment
upgrades ($15M), facility renovation ($12M), and IT infrastructure ($8M). The hospital maintains
a cash reserve of 90 days of operating expenses as recommended by the financial advisory board.
Outstanding accounts receivable total $62 million with an average collection period of 48 days.
The profit margin for the previous fiscal year was 3.2%, meeting the target set by the board of directors.
"""}
        ]
    },
    {
        "filename": "athletic_training_program.pdf",
        "pages": [
            {"type": "Sports", "content": """
<b>Elite Athletic Training and Development Program</b><br/><br/>
The comprehensive training program is designed to optimize athlete performance across multiple
sports disciplines. Each player undergoes a baseline fitness assessment including VO2 max testing,
body composition analysis, flexibility screening, and sport-specific skill evaluations. Training
periodization follows a 16-week macrocycle divided into preparation, competition, and recovery phases.<br/><br/>
<b>Strength and Conditioning:</b> Athletes participate in 4-5 strength training sessions per week
during the off-season, reduced to 2-3 sessions during the competitive season. The coaching staff
utilizes data-driven performance metrics including GPS tracking, heart rate monitoring, and
biomechanical analysis to optimize training loads and prevent overtraining injuries.<br/><br/>
Team practice sessions are scheduled 5 days per week, with tactical preparation for upcoming matches
integrated into technical training. Video analysis of opponent strategies is conducted by the
coaching staff and presented during pre-match briefings. Tournament preparation includes simulated
competition environments and mental performance coaching.
"""},
            {"type": "Sports", "content": """
<b>Competition Calendar and League Regulations</b><br/><br/>
The competitive season runs from September through June, comprising 82 regular-season matches and
potential playoff rounds. Teams must register their roster with the league office 30 days before
the season opener. Player transfers during the mid-season trading window (January 15 - February 15)
require approval from both teams and league compliance review.<br/><br/>
<b>Referee and Officiating Standards:</b> All matches are officiated by league-certified referees
who undergo annual fitness and rules examinations. Penalty decisions are subject to video review
for all championship-level competitions. Teams are fined $25,000 for each documented instance of
unsportsmanlike conduct by players or coaching staff during matches.<br/><br/>
Stadium requirements include a minimum seating capacity of 18,000 for top-division teams, with
adequate facilities for broadcast media, team operations, and spectator safety. Scoreboard and
timing systems must meet league technical specifications.
"""},
            {"type": "Medical", "content": """
<b>Sports Medicine and Injury Prevention</b><br/><br/>
The sports medicine department provides comprehensive healthcare services for all team athletes.
Pre-participation physical examinations include cardiac screening with electrocardiogram (ECG),
musculoskeletal assessment, and baseline neurocognitive testing for concussion management. Each
player's medical history is reviewed by the team physician before clearance for training and competition.<br/><br/>
Common sports injuries including ACL tears, rotator cuff injuries, and stress fractures are managed
through evidence-based treatment protocols. Rehabilitation programs are individually designed by
physical therapists and monitored through objective functional assessments. Return-to-play decisions
require clearance from the attending physician and must meet sport-specific functional criteria.
Anti-doping compliance follows World Anti-Doping Agency (WADA) guidelines with random testing during
competition and out-of-competition periods.
"""}
        ]
    },
    {
        "filename": "corporate_annual_report.pdf",
        "pages": [
            {"type": "Finance", "content": """
<b>Annual Financial Report - Fiscal Year 2024</b><br/><br/>
Total consolidated revenue for the fiscal year reached $1.28 billion, representing a 9.4% increase
year-over-year. Net income after tax was $142 million, with earnings per share (EPS) of $3.85.
The gross profit margin improved to 42.3% from 39.8% in the prior year, reflecting improved
operational efficiency and favorable product mix.<br/><br/>
<b>Segment Performance:</b> The healthcare division contributed $520 million in revenue (41% of total),
the technology segment generated $380 million (30%), and the consumer products division accounted
for $380 million (29%). Operating income by segment was $78M, $95M, and $45M respectively.<br/><br/>
Capital allocation priorities include $180 million in share buybacks, $65 million in dividend
payments (representing a 3.2% yield), and $120 million in research and development investment.
The balance sheet reflects total assets of $3.2 billion, stockholders' equity of $1.8 billion,
and a current ratio of 2.1. Long-term debt obligations total $450 million with a weighted average
interest rate of 4.15% and a credit rating of A- from Standard & Poor's.
"""},
            {"type": "Finance", "content": """
<b>Tax Strategy and Regulatory Compliance</b><br/><br/>
The effective tax rate for the fiscal year was 21.8%, compared to the statutory rate of 25%.
Tax benefits were derived from R&D tax credits ($12 million), foreign income tax provisions
($8 million), and accelerated depreciation on capital assets ($5 million). Deferred tax assets
of $45 million relate primarily to employee benefit accruals and warranty reserves.<br/><br/>
The company maintains compliance with all applicable financial regulations including SOX 404
internal controls, SEC reporting requirements, and international financial reporting standards
(IFRS) for foreign subsidiaries. The audit committee oversees quarterly financial reviews and
annual external audit conducted by a Big Four accounting firm. Risk management practices include
currency hedging for international operations, interest rate swaps on variable-rate debt, and
commodity futures contracts for raw material procurement.
"""},
            {"type": "Medical", "content": """
<b>Healthcare Division Performance</b><br/><br/>
The healthcare division launched three new medical devices during the fiscal year, including an
advanced patient monitoring system, a portable diagnostic imaging unit, and an automated medication
dispensing platform. Clinical trials for a next-generation surgical robot are progressing through
Phase III with FDA submission planned for Q2 2025.<br/><br/>
Revenue from hospital and clinical customers grew 14% year-over-year, driven by increased adoption
of telemedicine platforms and remote patient monitoring solutions. The division holds 45 active
patents in medical device technology and pharmaceutical delivery systems. Healthcare regulatory
compliance costs totaled $18 million, covering FDA inspections, CE marking for European markets,
and quality management system certifications.
"""}
        ]
    },
    {
        "filename": "sports_facility_development.pdf",
        "pages": [
            {"type": "Sports", "content": """
<b>Multi-Sport Facility Development Project</b><br/><br/>
The proposed sports complex encompasses a 45,000-seat main stadium, indoor training arena, aquatic
center, and athlete village. The facility is designed to host international-level competitions
including track and field championships, football tournaments, and swimming meets. The stadium
features a retractable roof system and FIFA-standard natural grass pitch with undersoil heating.<br/><br/>
Training facilities include 6 outdoor practice fields, a 200-meter indoor track, strength and
conditioning center with 15,000 sq ft of equipment space, and recovery facilities including
hydrotherapy pools and cryotherapy chambers. The coaching staff offices, video analysis rooms,
and team meeting spaces occupy the second floor of the training complex. Player locker rooms
accommodate up to 60 athletes with individual stations for equipment storage.
"""},
            {"type": "Finance", "content": """
<b>Project Financing and Budget</b><br/><br/>
Total project cost is estimated at $780 million, financed through a combination of municipal bonds
($350M), private investment ($280M), and federal sports infrastructure grants ($150M). The loan
terms include a 25-year amortization at 3.85% fixed interest rate with semi-annual payments.
Revenue projections for the completed facility include $45 million annually from event hosting,
$28 million from naming rights and sponsorship agreements, and $15 million from concessions and
merchandise sales.<br/><br/>
The operating budget for facility management is projected at $32 million per year, covering staff
salaries, maintenance, utilities, and insurance. Break-even is expected within 8 years of facility
opening. Tax increment financing (TIF) from surrounding commercial development is projected to
generate an additional $12 million annually. The capital budget includes a $25 million reserve
fund for equipment replacement and facility upgrades over the first decade of operations.
"""},
            {"type": "Sports", "content": """
<b>Community Sports Programs and League Partnerships</b><br/><br/>
The facility will serve as the home venue for three professional sports teams and host regional
amateur tournaments throughout the year. Youth development programs will provide training
opportunities for athletes aged 8-18 across multiple sports disciplines. The coaching academy
will offer certification courses for aspiring coaches in partnership with national sports federations.<br/><br/>
League partnerships include hosting rights for national championship events, pre-season training
camps for visiting teams, and referee development workshops. The facility's sport science laboratory
will provide performance testing services for collegiate and professional athletes. Annual
competitions including marathon events, triathlon championships, and inter-school tournaments
will utilize the multi-sport venue capabilities. Player development pathways connect youth
programs with professional team scouting networks.
"""}
        ]
    },
    {
        "filename": "insurance_claims_analysis.pdf",
        "pages": [
            {"type": "Medical", "content": """
<b>Medical Insurance Claims Analysis - 2024 Report</b><br/><br/>
Total medical claims processed during the fiscal year numbered 245,000 with a combined value of
$892 million. The average claim amount was $3,641, with the highest concentration in the $1,000-$5,000
range (42% of claims). Inpatient hospital claims averaged $18,500 per admission, while outpatient
procedure claims averaged $2,100.<br/><br/>
<b>Claims by Diagnosis Category:</b> Cardiovascular disease claims represented 18% of total expenditure,
followed by musculoskeletal disorders (15%), mental health services (12%), cancer treatment (11%),
and respiratory conditions (8%). The clinical review team identified $28 million in potentially
fraudulent claims requiring investigation. Pre-existing condition exclusions applied to 3.2% of
submitted claims. Prescription medication claims totaled $165 million, with specialty pharmacy
drugs accounting for 45% of pharmaceutical spending despite representing only 2% of prescriptions.
"""},
            {"type": "Finance", "content": """
<b>Claims Financial Impact and Reserve Analysis</b><br/><br/>
The loss ratio for the medical insurance line was 78.3%, within the target range of 75-82%.
Incurred but not reported (IBNR) reserves are estimated at $45 million based on actuarial analysis.
The claims reserve adequacy ratio is 112%, indicating sufficient reserves to cover outstanding
obligations. Investment income from claims reserves totaled $14.2 million at an average yield of 4.8%.<br/><br/>
Reinsurance recoveries for catastrophic claims exceeding $500,000 per individual totaled $22 million
from three reinsurance treaties. The combined ratio of 92.4% reflects underwriting profitability
for the medical insurance segment. Budget projections for the next fiscal year anticipate a 7%
increase in claims costs driven by medical inflation and expanded coverage mandates. Cash flow
from premium collections provides adequate liquidity with a current ratio of 3.2 for claims payment.
"""},
            {"type": "Medical", "content": """
<b>Quality Metrics and Patient Outcomes</b><br/><br/>
Healthcare quality metrics tracked through claims data reveal a 30-day hospital readmission rate of
8.2%, below the national average of 11.5%. Patient satisfaction scores averaged 4.2 out of 5.0
across network providers. Preventive care utilization rates show 72% of eligible members completed
annual wellness visits, and 68% received age-appropriate cancer screenings.<br/><br/>
Chronic disease management program enrollment reached 45,000 members with documented improvements
in clinical outcomes: HbA1c levels improved by an average of 1.2% in diabetic patients, blood
pressure control rates increased by 15% for hypertensive patients, and emergency department
utilization decreased by 22% among enrolled members. The physician network includes 12,000
contracted providers across 850 facilities. Telemedicine visit volume increased 45% year-over-year,
with patient-reported symptom resolution rates comparable to in-person consultations.
"""}
        ]
    },
    {
        "filename": "multi_sector_policy.pdf",
        "pages": [
            {"type": "Medical", "content": """
<b>Integrated Wellness and Healthcare Benefits</b><br/><br/>
Employees are entitled to comprehensive healthcare benefits including medical, dental, and vision
coverage. The standard medical plan covers 80% of in-network physician visits with a $30 copay.
Specialist referrals require authorization from the primary care physician. Annual preventive
health screenings including blood pressure monitoring, cholesterol testing, and cancer screening
are covered at 100% with no cost-sharing.<br/><br/>
Mental health benefits include 20 therapy sessions per year with licensed psychologists and
psychiatrists. Employee Assistance Program (EAP) provides confidential counseling services for
substance abuse, stress management, and family issues. Prescription drug coverage includes a
three-tier formulary with $10 generic, $35 preferred brand, and $60 non-preferred brand copays.
Mail-order pharmacy services offer 90-day supplies at reduced copays for maintenance medications.
"""},
            {"type": "Sports", "content": """
<b>Corporate Wellness and Sports Programs</b><br/><br/>
The company sponsors employee sports leagues including basketball, soccer, and softball teams.
Monthly fitness challenges with performance tracking encourage physical activity among all
employees. The corporate wellness center features a gymnasium with modern training equipment,
group fitness classes, and personal coaching sessions available to all staff members.<br/><br/>
Annual company-wide sports tournaments include a 5K charity run, inter-department volleyball
championship, and golf tournament. Employee athletes representing the company in external
competitions receive up to $2,500 in sponsorship funding. The fitness program includes partnerships
with local gyms offering discounted membership rates and specialized training sessions for team
sports participants. Corporate box seats at the city stadium are available for employee appreciation
events during professional league matches.
"""},
            {"type": "Finance", "content": """
<b>Compensation and Financial Benefits</b><br/><br/>
The total compensation package includes base salary, performance bonuses, and long-term equity
incentives. Annual merit increases are budgeted at 3.5% of the total payroll, with performance-based
bonuses ranging from 10-25% of base salary. The 401(k) retirement plan offers employer matching
of 100% on the first 6% of employee contributions with immediate vesting.<br/><br/>
Employee stock purchase program allows participation at a 15% discount to market price with
bi-annual purchase periods. Financial planning services are provided through a partnership with
a certified financial advisory firm. Tuition reimbursement covers up to $10,000 per year for
job-related education. The profit-sharing plan distributes 5% of annual net income to eligible
employees based on tenure and performance ratings. Tax-advantaged flexible spending accounts
(FSA) are available for healthcare and dependent care expenses with a $2,850 annual limit.
"""}
        ]
    },
    {
        "filename": "research_clinical_trials.pdf",
        "pages": [
            {"type": "Medical", "content": """
<b>Clinical Research Protocol - Phase III Randomized Controlled Trial</b><br/><br/>
This multi-center clinical trial evaluates the efficacy and safety of a novel therapeutic agent
for the treatment of Type 2 Diabetes Mellitus. The study enrolls 2,400 patients across 45 clinical
sites with a 52-week treatment duration. Primary endpoints include reduction in HbA1c levels,
fasting plasma glucose, and body weight from baseline.<br/><br/>
<b>Patient Eligibility Criteria:</b> Adults aged 18-75 with confirmed diagnosis of Type 2 diabetes,
HbA1c between 7.5% and 10.5%, and BMI between 25 and 40 kg/m². Exclusion criteria include
pregnancy, severe renal impairment (eGFR < 30), active liver disease, and history of diabetic
ketoacidosis. All patients provide written informed consent before enrollment. The clinical
research team includes board-certified endocrinologists, research nurses, and study coordinators
at each participating hospital site.
"""},
            {"type": "Medical", "content": """
<b>Safety Monitoring and Adverse Event Reporting</b><br/><br/>
An independent Data Safety Monitoring Board (DSMB) conducts interim safety analyses at 13, 26,
and 39 weeks. Serious adverse events (SAEs) must be reported to the FDA within 15 calendar days
of discovery. The most commonly reported symptoms include nausea (12%), headache (8%), and mild
hypoglycemia (6%).<br/><br/>
Laboratory monitoring includes monthly assessments of hepatic function (ALT, AST, bilirubin),
renal function (creatinine, eGFR), and complete blood count. Electrocardiogram (ECG) monitoring
is performed at screening, week 12, week 26, and end-of-treatment visits. All clinical data is
captured in a validated electronic data capture (EDC) system with 21 CFR Part 11 compliance.
The physician investigators must complete Good Clinical Practice (GCP) training and maintain
current medical licensure throughout the study period. Patient medical records are maintained
in accordance with HIPAA privacy regulations.
"""},
            {"type": "Finance", "content": """
<b>Clinical Trial Budget and Funding</b><br/><br/>
Total trial budget is $48 million, funded through the pharmaceutical company's R&D allocation
($38M) and collaborative research grants from the National Institutes of Health ($10M). Per-patient
costs average $20,000, covering investigator fees, laboratory analyses, study drug supply, and
monitoring visits. Site payments are structured as $5,000 per enrolled patient plus $800 per
completed study visit.<br/><br/>
Contract research organization (CRO) fees total $12 million for data management, statistical
analysis, regulatory submissions, and pharmacovigilance services. The revenue potential for the
drug under investigation is estimated at $3.5 billion annually upon FDA approval, based on market
analysis and competitive landscape assessment. Patent protection extends through 2038, providing
14 years of market exclusivity. Capital investment in manufacturing scale-up is budgeted at
$200 million for production facility construction and FDA inspection readiness.
"""}
        ]
    }
]


def create_pdf(doc_data: dict, output_dir: str):
    """Create a single PDF document from the template data."""
    filepath = os.path.join(output_dir, doc_data["filename"])
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            topMargin=72, bottomMargin=72,
                            leftMargin=72, rightMargin=72)

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "CustomBody", parent=styles["Normal"],
        fontSize=11, leading=16, spaceAfter=12
    )
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=16, spaceAfter=24
    )

    story = []

    for i, page_data in enumerate(doc_data["pages"]):
        if i > 0:
            story.append(PageBreak())

        content = page_data["content"].strip()
        story.append(Paragraph(content, body_style))
        story.append(Spacer(1, 12))

    doc.build(story)
    print(f"  Created: {filepath}")
    return filepath


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating {len(DOCUMENTS)} sample PDFs in {OUTPUT_DIR}...")

    for doc_data in DOCUMENTS:
        create_pdf(doc_data, OUTPUT_DIR)

    print(f"\nDone! {len(DOCUMENTS)} PDFs generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
