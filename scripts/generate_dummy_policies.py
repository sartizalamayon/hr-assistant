"""Generate two realistic dummy HR policy PDFs for testing the RAG pipeline.

These are placeholder documents for a fictional company ("Acme Corporation")
that mirror the structure of real HR policy PDFs (title, main headings,
subheadings, body paragraphs, rules/exceptions, and examples), so they can be
swapped for real documents later without changing the app.

Run with: python -m scripts.generate_dummy_policies
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_docs")

COMPANY = "Acme Corporation"
ACCENT = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
EXAMPLE_BG = colors.HexColor("#f3f4f6")

styles = getSampleStyleSheet()

doc_title_style = ParagraphStyle(
    "DocTitle", parent=styles["Title"], fontSize=22, spaceAfter=4, textColor=ACCENT,
)
doc_subtitle_style = ParagraphStyle(
    "DocSubtitle", parent=styles["Normal"], fontSize=10, textColor=MUTED, spaceAfter=20,
)
h1_style = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontSize=15, spaceBefore=22, spaceAfter=8,
    textColor=ACCENT, borderColor=ACCENT, borderWidth=0,
)
h2_style = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontSize=12, spaceBefore=14, spaceAfter=6,
    textColor=colors.HexColor("#374151"),
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"], fontSize=10, leading=15, spaceAfter=8,
    alignment=TA_JUSTIFY,
)
bullet_style = ParagraphStyle(
    "Bullet", parent=body_style, spaceAfter=3,
)
example_label_style = ParagraphStyle(
    "ExampleLabel", parent=body_style, fontSize=9, textColor=ACCENT, spaceAfter=2,
    fontName="Helvetica-Bold",
)
example_style = ParagraphStyle(
    "Example", parent=body_style, fontSize=9.5, textColor=colors.HexColor("#374151"),
    spaceAfter=0, fontName="Helvetica-Oblique",
)


def section(heading, body_paragraphs=None, bullets=None, subsections=None, example=None):
    """Build a list of flowables for one H1 section, optional bullets/example/subsections."""
    flow = [Paragraph(heading, h1_style), HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#d1d5db"), spaceAfter=8)]
    flow += _body_block(body_paragraphs, bullets, example)
    for sub in subsections or []:
        flow.append(Paragraph(sub["heading"], h2_style))
        flow += _body_block(sub.get("body"), sub.get("bullets"), sub.get("example"))
    return flow


def _body_block(body_paragraphs, bullets, example):
    flow = []
    for para in body_paragraphs or []:
        flow.append(Paragraph(para, body_style))
    if bullets:
        flow.append(
            ListFlowable(
                [ListItem(Paragraph(b, bullet_style), leftIndent=6) for b in bullets],
                bulletType="bullet",
                start="•",
                leftIndent=16,
            )
        )
        flow.append(Spacer(1, 6))
    if example:
        table = Table(
            [[Paragraph("EXAMPLE", example_label_style)], [Paragraph(example, example_style)]],
            colWidths=[6.3 * inch],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), EXAMPLE_BG),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (0, 0), 6),
                    ("BOTTOMPADDING", (0, 0), (0, 0), 0),
                    ("TOPPADDING", (0, 1), (0, 1), 2),
                    ("BOTTOMPADDING", (0, 1), (0, 1), 8),
                ]
            )
        )
        flow.append(table)
        flow.append(Spacer(1, 6))
    return flow


def make_doc(filename, title, subtitle, sections_data):
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        path,
        pagesize=LETTER,
        topMargin=0.9 * inch,
        bottomMargin=0.8 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        title=title,
        author=COMPANY,
    )

    def add_footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.9 * inch, 0.5 * inch, f"{COMPANY} — Confidential — Internal Use Only")
        canvas.drawRightString(LETTER[0] - 0.9 * inch, 0.5 * inch, f"Page {doc_.page}")
        canvas.restoreState()

    story = [
        Paragraph(title, doc_title_style),
        Paragraph(subtitle, doc_subtitle_style),
    ]
    for sec in sections_data:
        story += section(**sec)

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Document 1: Leave Policy
# ---------------------------------------------------------------------------
leave_policy_sections = [
    dict(
        heading="1. Purpose and Scope",
        body_paragraphs=[
            f"This Leave Policy outlines the types of leave available to employees of {COMPANY} "
            "(\"the Company\"), the eligibility requirements for each, and the process for requesting "
            "time away from work. It applies to all full-time and part-time employees, unless a "
            "specific section states otherwise.",
            "Managers and employees are jointly responsible for planning leave in a way that "
            "minimizes disruption to business operations. Nothing in this policy overrides "
            "statutory leave entitlements in the employee's jurisdiction of employment; where local "
            "law provides greater benefits than this policy, local law applies.",
        ],
    ),
    dict(
        heading="2. Annual Leave (Vacation)",
        subsections=[
            dict(
                heading="2.1 Accrual and Entitlement",
                body=[
                    "Full-time employees accrue 15 days of paid annual leave per calendar year, "
                    "credited monthly at a rate of 1.25 days per full month of service. Part-time "
                    "employees accrue leave on a pro-rated basis according to their contracted hours.",
                    "New employees begin accruing leave from their first day of employment but may "
                    "not take annual leave during their first 90 days, except with manager approval.",
                ],
            ),
            dict(
                heading="2.2 Requesting Leave",
                body=[
                    "Employees must submit annual leave requests through the HR portal at least 10 "
                    "business days in advance. Requests are approved at the manager's discretion, "
                    "taking into account team workload and prior commitments.",
                ],
                bullets=[
                    "Requests of 5 consecutive working days or more require 4 weeks' notice.",
                    "Leave taken around major public holidays may be subject to blackout periods "
                    "communicated by the department head.",
                    "Unapproved absences are treated as unauthorized leave and may be subject to "
                    "disciplinary action.",
                ],
            ),
            dict(
                heading="2.3 Carryover and Forfeiture",
                body=[
                    "Employees may carry over a maximum of 5 unused annual leave days into the "
                    "following calendar year. Carried-over days must be used by March 31 of the new "
                    "year, after which they are forfeited. Exceptions may be granted where an "
                    "employee was unable to take leave due to approved extended sick leave or "
                    "parental leave in the preceding year.",
                ],
                example=(
                    "Priya has 4 unused vacation days on December 31. All 4 days carry over "
                    "automatically. She must use them by March 31 or they will be forfeited, "
                    "unless she was on approved medical leave during that window."
                ),
            ),
        ],
    ),
    dict(
        heading="3. Sick Leave",
        subsections=[
            dict(
                heading="3.1 Entitlement",
                body=[
                    "Employees receive 10 paid sick days per calendar year. Unused sick days do not "
                    "roll over to the following year and are not paid out upon termination.",
                ],
            ),
            dict(
                heading="3.2 Notification Requirements",
                body=[
                    "Employees who are unable to work due to illness must notify their manager before "
                    "their normal start time, or as soon as reasonably possible. Notification may be "
                    "made by phone, email, or the messaging channel designated by the team.",
                ],
            ),
            dict(
                heading="3.3 Medical Certification",
                body=[
                    "A doctor's note is required for any sick leave lasting more than 3 consecutive "
                    "working days. HR reserves the right to request medical certification for "
                    "shorter absences where a pattern of frequent short-term absence is observed.",
                ],
            ),
            dict(
                heading="3.4 Extended Illness",
                body=[
                    "Employees facing a serious or long-term illness should contact HR to discuss "
                    "extended sick leave, which may be granted beyond the standard 10-day entitlement "
                    "on an unpaid or partially paid basis, subject to applicable disability or "
                    "insurance benefits.",
                ],
            ),
        ],
    ),
    dict(
        heading="4. Parental Leave",
        subsections=[
            dict(
                heading="4.1 Maternity and Primary Caregiver Leave",
                body=[
                    "Employees who are the primary caregiver following the birth, adoption, or foster "
                    "placement of a child are entitled to 12 weeks of paid parental leave. Leave may "
                    "begin up to 2 weeks before the expected due date and must be taken within 12 "
                    "months of the child's arrival.",
                ],
            ),
            dict(
                heading="4.2 Paternity and Secondary Caregiver Leave",
                body=[
                    "Employees who are the secondary caregiver are entitled to 4 weeks of paid leave, "
                    "which may be taken continuously or split into two blocks within the first 6 "
                    "months following the child's arrival, subject to manager approval of scheduling.",
                ],
            ),
            dict(
                heading="4.3 Adoption and Foster Leave",
                body=[
                    "Adoptive and foster parents are eligible for the same entitlements as biological "
                    "parents described above, calculated from the date the child is placed with the "
                    "family rather than the date of birth.",
                ],
            ),
            dict(
                heading="4.4 Returning to Work",
                body=[
                    "Employees returning from parental leave are guaranteed reinstatement to their "
                    "same or an equivalent role, with no loss of seniority. Employees who wish to "
                    "request a phased return or flexible schedule should discuss this with HR at "
                    "least 2 weeks before their return date.",
                ],
                example=(
                    "Daniel takes 4 weeks of secondary caregiver leave after his partner gives "
                    "birth, splitting it into 2 weeks immediately after the birth and 2 weeks "
                    "three months later, both approved in advance by his manager."
                ),
            ),
        ],
    ),
    dict(
        heading="5. Sabbatical Leave",
        subsections=[
            dict(
                heading="5.1 Eligibility",
                body=[
                    "Employees with at least 5 years of continuous service are eligible to apply for "
                    "unpaid sabbatical leave of up to 3 months. Sabbatical leave is granted at the "
                    "discretion of senior management and is not guaranteed.",
                ],
            ),
            dict(
                heading="5.2 Application Process",
                body=[
                    "Applications must be submitted to HR at least 3 months in advance, outlining the "
                    "intended dates, purpose, and a handover plan for ongoing responsibilities. HR and "
                    "the employee's manager will respond within 4 weeks of submission.",
                ],
            ),
            dict(
                heading="5.3 Pay and Benefits During Sabbatical",
                body=[
                    "Sabbatical leave is unpaid. Health insurance benefits continue during the "
                    "sabbatical period, with the employee responsible for any portion of premiums "
                    "normally deducted from payroll. Annual leave and sick leave do not accrue "
                    "during a sabbatical.",
                ],
            ),
        ],
    ),
    dict(
        heading="6. Other Leave Types",
        subsections=[
            dict(
                heading="6.1 Bereavement Leave",
                body=[
                    "Employees are entitled to 5 paid days of bereavement leave following the death "
                    "of an immediate family member (spouse, child, parent, or sibling), and 2 paid "
                    "days for the death of an extended family member.",
                ],
            ),
            dict(
                heading="6.2 Jury Duty and Civic Leave",
                body=[
                    "Employees summoned for jury duty or required to appear in court as a witness "
                    "will be granted paid leave for the duration of their service, upon presentation "
                    "of the official summons to HR.",
                ],
            ),
            dict(
                heading="6.3 Unpaid Personal Leave",
                body=[
                    "Employees who have exhausted other applicable leave types may request unpaid "
                    "personal leave of up to 4 weeks per calendar year, subject to manager and HR "
                    "approval based on business needs.",
                ],
            ),
            dict(
                heading="6.4 Public Holidays",
                body=[
                    "The Company observes 10 paid public holidays per year, as published annually on "
                    "the HR portal. Employees required to work on a public holiday will receive a "
                    "substitute day off within 30 days or premium pay, per local requirements.",
                ],
            ),
        ],
    ),
    dict(
        heading="7. General Provisions",
        subsections=[
            dict(
                heading="7.1 Leave Approval Process",
                body=[
                    "All leave requests, regardless of type, are submitted and tracked through the "
                    "HR portal. Verbal approval from a manager does not replace the need for a "
                    "formal request record.",
                ],
            ),
            dict(
                heading="7.2 Policy Review",
                body=[
                    "This policy is reviewed annually by HR and may be updated to reflect changes in "
                    "employment law or business needs. Employees will be notified of material changes "
                    "at least 30 days before they take effect.",
                ],
            ),
        ],
    ),
]

# ---------------------------------------------------------------------------
# Document 2: Employee Handbook
# ---------------------------------------------------------------------------
handbook_sections = [
    dict(
        heading="1. Welcome and Purpose",
        body_paragraphs=[
            f"Welcome to {COMPANY}. This Employee Handbook describes the policies, benefits, and "
            "standards of conduct that apply to all employees. It is intended as a general guide "
            "and does not constitute an employment contract.",
            "Where a specific policy document (such as the Leave Policy) provides more detailed "
            "rules on a topic covered briefly here, that dedicated policy takes precedence.",
        ],
    ),
    dict(
        heading="2. Employment Basics",
        subsections=[
            dict(
                heading="2.1 Employment Classification",
                body=[
                    "Employees are classified as full-time (35+ hours per week), part-time, or "
                    "temporary/contract. Classification determines eligibility for certain benefits "
                    "as described in Section 3.",
                ],
            ),
            dict(
                heading="2.2 Working Hours and Attendance",
                body=[
                    "Standard working hours are 9:00 AM to 5:30 PM, Monday through Friday, with a "
                    "30-minute unpaid lunch break. Departments with different operational needs may "
                    "set alternative schedules with HR approval.",
                    "Employees are expected to notify their manager as soon as possible if they will "
                    "be late or unable to attend work for reasons other than pre-approved leave.",
                ],
            ),
            dict(
                heading="2.3 Overtime",
                body=[
                    "Non-exempt employees who work beyond 40 hours in a week are eligible for "
                    "overtime pay at 1.5 times their regular hourly rate, subject to prior manager "
                    "approval. Exempt (salaried) employees are not eligible for overtime pay but may "
                    "be granted compensatory time off at manager discretion.",
                ],
                example=(
                    "Maria, a non-exempt customer support associate, works 44 hours in a week with "
                    "her manager's approval. She is paid her regular rate for 40 hours and 1.5x her "
                    "rate for the additional 4 hours."
                ),
            ),
        ],
    ),
    dict(
        heading="3. Compensation and Benefits",
        subsections=[
            dict(
                heading="3.1 Payroll and Pay Schedule",
                body=[
                    "Employees are paid on a bi-weekly basis via direct deposit. Pay statements are "
                    "available through the HR portal on the Wednesday preceding each pay date.",
                ],
            ),
            dict(
                heading="3.2 Health Insurance",
                body=[
                    "Full-time employees are eligible for company-subsidized health, dental, and "
                    "vision insurance starting on the first day of the month following 30 days of "
                    "employment. The Company covers 80% of the premium for employee-only coverage.",
                ],
            ),
            dict(
                heading="3.3 Retirement Savings Plan",
                body=[
                    "Employees may enroll in the Company's retirement savings plan after 90 days of "
                    "employment. The Company matches employee contributions up to 4% of base salary.",
                ],
            ),
            dict(
                heading="3.4 Other Perks",
                body=[
                    "Additional benefits include an annual $500 learning and development stipend, a "
                    "$50 monthly wellness allowance, and an employee assistance program providing "
                    "confidential counseling services.",
                ],
            ),
        ],
    ),
    dict(
        heading="4. Code of Conduct",
        subsections=[
            dict(
                heading="4.1 Professional Behavior",
                body=[
                    "Employees are expected to treat colleagues, clients, and partners with respect "
                    "and professionalism at all times, both in the workplace and at company-sponsored "
                    "events.",
                ],
            ),
            dict(
                heading="4.2 Anti-Harassment and Non-Discrimination",
                body=[
                    "The Company maintains a strict zero-tolerance policy toward harassment, "
                    "discrimination, or retaliation of any kind based on race, gender, age, religion, "
                    "disability, sexual orientation, or any other protected characteristic. Employees "
                    "who experience or witness such conduct should report it to HR immediately; all "
                    "reports are treated confidentially and investigated promptly.",
                ],
            ),
            dict(
                heading="4.3 Conflicts of Interest",
                body=[
                    "Employees must disclose to HR any outside employment, financial interest, or "
                    "personal relationship that could reasonably be seen to conflict with the "
                    "Company's interests, including relationships with vendors, competitors, or "
                    "direct reports.",
                ],
            ),
            dict(
                heading="4.4 Confidentiality",
                body=[
                    "Employees must not disclose confidential business information, trade secrets, "
                    "or personal data of employees or customers to any unauthorized party, both "
                    "during and after their employment with the Company.",
                ],
            ),
        ],
    ),
    dict(
        heading="5. Workplace Policies",
        subsections=[
            dict(
                heading="5.1 Dress Code",
                body=[
                    "The Company follows a business-casual dress code on standard working days. "
                    "Employees meeting with external clients or attending formal events should dress "
                    "in business professional attire. Casual dress, including jeans, is permitted on "
                    "Fridays.",
                ],
            ),
            dict(
                heading="5.2 Remote and Hybrid Work",
                body=[
                    "Employees may work remotely up to 2 days per week with manager approval. Fully "
                    "remote arrangements require sign-off from a department VP and are evaluated on a "
                    "case-by-case basis considering role requirements and team needs.",
                ],
                bullets=[
                    "Remote work days must be logged in the HR portal.",
                    "Employees are expected to be reachable during core hours (10:00 AM–4:00 PM) "
                    "regardless of work location.",
                    "The Company is not responsible for providing home office furniture, but offers "
                    "a one-time $200 home office stipend for new hires.",
                ],
            ),
            dict(
                heading="5.3 Use of Company Property and IT Systems",
                body=[
                    "Company equipment, email, and IT systems are provided for business use. Limited "
                    "personal use is permitted provided it does not interfere with work "
                    "responsibilities or violate the Acceptable Use Policy maintained by the IT "
                    "department.",
                ],
            ),
            dict(
                heading="5.4 Health and Safety",
                body=[
                    "The Company is committed to maintaining a safe working environment in compliance "
                    "with applicable workplace safety regulations. Employees must report any safety "
                    "hazards, accidents, or near-misses to their manager and the Facilities team "
                    "immediately.",
                ],
            ),
        ],
    ),
    dict(
        heading="6. Performance and Development",
        subsections=[
            dict(
                heading="6.1 Performance Reviews",
                body=[
                    "Formal performance reviews are conducted twice a year, in June and December. "
                    "Reviews assess progress against agreed goals and inform decisions on "
                    "compensation, promotion, and development planning.",
                ],
            ),
            dict(
                heading="6.2 Training and Development",
                body=[
                    "Employees are encouraged to pursue professional development opportunities "
                    "relevant to their role, supported by the annual learning stipend described in "
                    "Section 3.4 and internal training programs offered throughout the year.",
                ],
            ),
            dict(
                heading="6.3 Disciplinary Process",
                body=[
                    "Performance or conduct concerns are typically addressed through an informal "
                    "conversation in the first instance. Where issues persist, the Company follows a "
                    "progressive disciplinary process: verbal warning, written warning, final written "
                    "warning, and, if necessary, termination. Serious misconduct (such as theft, "
                    "harassment, or safety violations) may result in immediate termination without "
                    "progressing through earlier steps.",
                ],
            ),
        ],
    ),
    dict(
        heading="7. Separation from Employment",
        subsections=[
            dict(
                heading="7.1 Resignation",
                body=[
                    "Employees who wish to resign are asked to provide at least 4 weeks' written "
                    "notice to their manager and HR, to allow for an orderly handover of "
                    "responsibilities.",
                ],
            ),
            dict(
                heading="7.2 Termination",
                body=[
                    "The Company may terminate employment for reasons including, but not limited to, "
                    "performance, conduct, or business restructuring, in accordance with applicable "
                    "employment law and the disciplinary process described in Section 6.3.",
                ],
            ),
            dict(
                heading="7.3 Exit Process",
                body=[
                    "Departing employees are required to return all Company property, including "
                    "laptops, access cards, and any physical documents, on or before their last day. "
                    "HR will schedule an exit interview to gather feedback and confirm final pay and "
                    "benefits details.",
                ],
            ),
        ],
    ),
]


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    make_doc(
        "leave_policy.pdf",
        f"{COMPANY} — Leave Policy",
        "Human Resources Policy Document · Version 1.0 · Effective January 1, 2026",
        leave_policy_sections,
    )
    make_doc(
        "employee_handbook.pdf",
        f"{COMPANY} — Employee Handbook",
        "Human Resources Policy Document · Version 1.0 · Effective January 1, 2026",
        handbook_sections,
    )
