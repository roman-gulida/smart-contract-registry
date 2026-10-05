"""
Document Generator for Smart Contract Registry
Generates 100 PDF documents per class (Logistics, Salary, HR, Finance, Legal)
Total: 500 documents
"""

import os
import random
from datetime import datetime, timedelta
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

# Initialize Faker
fake = Faker()

# Output directory structure
OUTPUT_DIR = "data"
CLASSES = ["logistics", "salary", "hr", "finance", "legal"]


def ensure_directories():
    """Create output directories for each document class"""
    for doc_class in CLASSES:
        os.makedirs(os.path.join(OUTPUT_DIR, doc_class), exist_ok=True)


def random_date(start_days_ago=365, end_days_ago=0):
    """Generate a random date within the past year"""
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    return start + (end - start) * random.random()


# LOGISTICS DOCUMENTS
def generate_logistics_document(index):
    """Generate a logistics document (shipping receipt, delivery note, inventory)"""
    filename = os.path.join(OUTPUT_DIR, "logistics", f"logistics_{index:03d}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title style
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    # Randomize document type
    doc_types = [
        "Shipping Receipt",
        "Delivery Note",
        "Inventory Report",
        "Warehouse Transfer",
    ]
    doc_type = random.choice(doc_types)

    # Header
    story.append(Paragraph(doc_type, title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Document details
    tracking_number = fake.bothify(text="TRK-####-????").upper()
    ship_date = random_date(60, 1).strftime("%Y-%m-%d")

    details = [
        ["Tracking Number:", tracking_number],
        ["Date:", ship_date],
        ["Origin:", f"{fake.city()}, {fake.state_abbr()}"],
        ["Destination:", f"{fake.city()}, {fake.state_abbr()}"],
        ["Carrier:", random.choice(["FedEx", "UPS", "DHL", "USPS", "Local Courier"])],
    ]

    details_table = Table(details, colWidths=[2 * inch, 4 * inch])
    details_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(details_table)
    story.append(Spacer(1, 0.3 * inch))

    # Items table
    story.append(Paragraph("<b>Shipped Items</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    items_data = [["Item", "SKU", "Quantity", "Weight (lbs)"]]
    num_items = random.randint(3, 8)

    for _ in range(num_items):
        items_data.append(
            [
                fake.catch_phrase(),
                fake.bothify(text="SKU-#####"),
                str(random.randint(1, 50)),
                f"{random.randint(5, 100)}.{random.randint(0, 99):02d}",
            ]
        )

    items_table = Table(
        items_data, colWidths=[2.5 * inch, 1.5 * inch, 1 * inch, 1 * inch]
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 0.3 * inch))

    # Notes
    story.append(
        Paragraph(f"<b>Notes:</b> {fake.sentence(nb_words=10)}", styles["Normal"])
    )

    doc.build(story)
    return filename


# SALARY DOCUMENTS
def generate_salary_document(index):
    """Generate a salary slip/payroll document"""
    filename = os.path.join(OUTPUT_DIR, "salary", f"salary_{index:03d}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    story.append(Paragraph("Salary Slip", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Employee details
    employee_name = fake.name()
    employee_id = fake.bothify(text="EMP-####")
    pay_period = random_date(90, 30).strftime("%B %Y")

    emp_details = [
        ["Employee Name:", employee_name],
        ["Employee ID:", employee_id],
        [
            "Department:",
            random.choice(["Engineering", "Sales", "Marketing", "Operations", "HR"]),
        ],
        ["Position:", fake.job()],
        ["Pay Period:", pay_period],
    ]

    emp_table = Table(emp_details, colWidths=[2 * inch, 4 * inch])
    emp_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(emp_table)
    story.append(Spacer(1, 0.3 * inch))

    # Earnings
    story.append(Paragraph("<b>Earnings</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.1 * inch))

    base_salary = random.randint(3000, 10000)
    bonus = random.randint(0, 2000)
    allowance = random.randint(200, 800)

    earnings_data = [
        ["Description", "Amount"],
        ["Basic Salary", f"${base_salary:,.2f}"],
        ["Performance Bonus", f"${bonus:,.2f}"],
        ["Allowances", f"${allowance:,.2f}"],
    ]

    gross_salary = base_salary + bonus + allowance

    earnings_table = Table(earnings_data, colWidths=[3 * inch, 2 * inch])
    earnings_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(earnings_table)
    story.append(Spacer(1, 0.2 * inch))

    # Deductions
    story.append(Paragraph("<b>Deductions</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.1 * inch))

    tax = gross_salary * 0.22
    insurance = random.randint(150, 400)
    retirement = gross_salary * 0.05

    deductions_data = [
        ["Description", "Amount"],
        ["Federal Tax", f"${tax:,.2f}"],
        ["Health Insurance", f"${insurance:,.2f}"],
        ["401(k) Contribution", f"${retirement:,.2f}"],
    ]

    total_deductions = tax + insurance + retirement

    deductions_table = Table(deductions_data, colWidths=[3 * inch, 2 * inch])
    deductions_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e74c3c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(deductions_table)
    story.append(Spacer(1, 0.3 * inch))

    # Net Pay
    net_pay = gross_salary - total_deductions
    net_pay_data = [
        ["Gross Salary:", f"${gross_salary:,.2f}"],
        ["Total Deductions:", f"${total_deductions:,.2f}"],
        ["Net Pay:", f"${net_pay:,.2f}"],
    ]

    net_table = Table(net_pay_data, colWidths=[3 * inch, 2 * inch])
    net_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LINEABOVE", (0, 2), (-1, 2), 2, colors.black),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#2ecc71")),
            ]
        )
    )
    story.append(net_table)

    doc.build(story)
    return filename


# HR DOCUMENTS
def generate_hr_document(index):
    """Generate HR documents (employment contract, leave application, performance review)"""
    filename = os.path.join(OUTPUT_DIR, "hr", f"hr_{index:03d}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Randomize HR document type
    doc_types = ["Employment Contract", "Leave Application", "Performance Review"]
    doc_type = random.choice(doc_types)

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#8e44ad"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    story.append(Paragraph(doc_type, title_style))
    story.append(Spacer(1, 0.2 * inch))

    employee_name = fake.name()
    document_date = random_date(180, 1).strftime("%Y-%m-%d")

    if doc_type == "Employment Contract":
        content = f"""
        <b>This Employment Agreement</b> is entered into on {document_date} between 
        <b>{fake.company()}</b> (the "Employer") and <b>{employee_name}</b> (the "Employee").
        <br/><br/>
        <b>1. Position:</b> The Employee is hired as {fake.job()}.
        <br/><br/>
        <b>2. Start Date:</b> Employment shall commence on {random_date(60, 30).strftime("%Y-%m-%d")}.
        <br/><br/>
        <b>3. Compensation:</b> The Employee shall receive an annual salary of 
        ${random.randint(50000, 120000):,}, payable in accordance with the Employer's standard payroll practices.
        <br/><br/>
        <b>4. Benefits:</b> The Employee shall be entitled to health insurance, retirement benefits, 
        and {random.randint(10, 25)} days of paid time off per year.
        <br/><br/>
        <b>5. Confidentiality:</b> The Employee agrees to maintain confidentiality of all proprietary 
        information and trade secrets of the Employer.
        <br/><br/>
        <b>6. Termination:</b> Either party may terminate this agreement with {random.randint(2, 4)} weeks' 
        written notice.
        """

    elif doc_type == "Leave Application":
        leave_types = [
            "Vacation",
            "Sick Leave",
            "Personal Leave",
            "Maternity/Paternity Leave",
        ]
        leave_type = random.choice(leave_types)
        start_date = random_date(60, 30).strftime("%Y-%m-%d")
        end_date = random_date(29, 1).strftime("%Y-%m-%d")

        content = f"""
        <b>Employee Name:</b> {employee_name}<br/>
        <b>Employee ID:</b> {fake.bothify(text="EMP-####")}<br/>
        <b>Department:</b> {random.choice(["Engineering", "Sales", "HR", "Operations"])}<br/>
        <b>Application Date:</b> {document_date}<br/><br/>
        
        <b>Leave Type:</b> {leave_type}<br/>
        <b>Start Date:</b> {start_date}<br/>
        <b>End Date:</b> {end_date}<br/>
        <b>Total Days:</b> {random.randint(1, 14)}<br/><br/>
        
        <b>Reason:</b><br/>
        {fake.paragraph(nb_sentences=3)}<br/><br/>
        
        <b>Emergency Contact:</b> {fake.phone_number()}<br/>
        <b>Email:</b> {fake.email()}<br/><br/>
        
        <b>Approved by:</b> ___________________<br/>
        <b>Date:</b> ___________________
        """

    else:  # Performance Review
        content = f"""
        <b>Employee Name:</b> {employee_name}<br/>
        <b>Position:</b> {fake.job()}<br/>
        <b>Review Period:</b> {random_date(365, 180).strftime("%B %Y")} - {random_date(179, 90).strftime("%B %Y")}<br/>
        <b>Review Date:</b> {document_date}<br/><br/>
        
        <b>Performance Rating:</b> {random.choice(["Excellent", "Good", "Satisfactory", "Needs Improvement"])}<br/><br/>
        
        <b>Key Achievements:</b><br/>
        • {fake.sentence(nb_words=8)}<br/>
        • {fake.sentence(nb_words=10)}<br/>
        • {fake.sentence(nb_words=7)}<br/><br/>
        
        <b>Areas for Improvement:</b><br/>
        • {fake.sentence(nb_words=9)}<br/>
        • {fake.sentence(nb_words=8)}<br/><br/>
        
        <b>Goals for Next Period:</b><br/>
        • {fake.sentence(nb_words=10)}<br/>
        • {fake.sentence(nb_words=9)}<br/>
        • {fake.sentence(nb_words=11)}<br/><br/>
        
        <b>Reviewer:</b> {fake.name()}<br/>
        <b>Signature:</b> ___________________
        """

    story.append(Paragraph(content, styles["Normal"]))

    doc.build(story)
    return filename


# FINANCE DOCUMENTS
def generate_finance_document(index):
    """Generate finance documents (invoices, receipts, expense reports)"""
    filename = os.path.join(OUTPUT_DIR, "finance", f"finance_{index:03d}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    doc_types = ["Invoice", "Receipt", "Expense Report"]
    doc_type = random.choice(doc_types)

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#27ae60"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    story.append(Paragraph(doc_type, title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Company details
    company_name = fake.company()
    invoice_number = fake.bothify(text="INV-####-????").upper()
    invoice_date = random_date(90, 1).strftime("%Y-%m-%d")

    company_details = [
        [f"{company_name}"],
        [fake.address().replace("\n", ", ")],
        [f"Phone: {fake.phone_number()}"],
        [f"Email: {fake.email()}"],
    ]

    company_table = Table(company_details, colWidths=[6 * inch])
    company_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(company_table)
    story.append(Spacer(1, 0.3 * inch))

    # Invoice details
    details_data = [
        [f"{doc_type} Number:", invoice_number],
        ["Date:", invoice_date],
        [
            "Due Date:",
            (datetime.strptime(invoice_date, "%Y-%m-%d") + timedelta(days=30)).strftime(
                "%Y-%m-%d"
            ),
        ],
    ]

    if doc_type == "Invoice":
        details_data.append(["Bill To:", fake.company()])

    details_table = Table(details_data, colWidths=[2 * inch, 4 * inch])
    details_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(details_table)
    story.append(Spacer(1, 0.3 * inch))

    # Line items
    story.append(Paragraph("<b>Items</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    items_data = [["Description", "Quantity", "Unit Price", "Total"]]
    num_items = random.randint(2, 6)
    subtotal = 0

    for _ in range(num_items):
        qty = random.randint(1, 20)
        unit_price = random.uniform(10, 500)
        total = qty * unit_price
        subtotal += total

        items_data.append(
            [fake.bs().title(), str(qty), f"${unit_price:.2f}", f"${total:.2f}"]
        )

    items_table = Table(
        items_data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 0.2 * inch))

    # Totals
    tax = subtotal * 0.08
    total = subtotal + tax

    totals_data = [
        ["Subtotal:", f"${subtotal:.2f}"],
        ["Tax (8%):", f"${tax:.2f}"],
        ["Total:", f"${total:.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[4.5 * inch, 1.5 * inch])
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, -1), (-1, -1), 12),
                ("LINEABOVE", (0, -1), (-1, -1), 2, colors.black),
            ]
        )
    )
    story.append(totals_table)
    story.append(Spacer(1, 0.3 * inch))

    # Payment terms
    story.append(Paragraph("<b>Payment Terms:</b> Net 30 days", styles["Normal"]))
    story.append(
        Paragraph(f"<b>Notes:</b> {fake.sentence(nb_words=12)}", styles["Normal"])
    )

    doc.build(story)
    return filename


# LEGAL DOCUMENTS
def generate_legal_document(index):
    """Generate legal documents (contracts, agreements, compliance docs)"""
    filename = os.path.join(OUTPUT_DIR, "legal", f"legal_{index:03d}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    doc_types = [
        "Service Agreement",
        "Non-Disclosure Agreement",
        "Compliance Certificate",
        "Partnership Agreement",
    ]
    doc_type = random.choice(doc_types)

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#c0392b"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    story.append(Paragraph(doc_type, title_style))
    story.append(Spacer(1, 0.2 * inch))

    party1 = fake.company()
    party2 = fake.company()
    agreement_date = random_date(365, 1).strftime("%Y-%m-%d")

    if doc_type == "Service Agreement":
        content = f"""
        <b>SERVICE AGREEMENT</b><br/><br/>
        
        This Service Agreement ("Agreement") is entered into as of {agreement_date} 
        by and between <b>{party1}</b> ("Provider") and <b>{party2}</b> ("Client").<br/><br/>
        
        <b>1. SERVICES</b><br/>
        Provider agrees to provide the following services: {fake.bs()}. The services shall be 
        performed in accordance with industry standards and best practices.<br/><br/>
        
        <b>2. TERM</b><br/>
        This Agreement shall commence on {agreement_date} and continue for a period of 
        {random.randint(6, 36)} months, unless terminated earlier in accordance with the terms herein.<br/><br/>
        
        <b>3. COMPENSATION</b><br/>
        Client agrees to pay Provider ${random.randint(5000, 50000):,} per month for the services rendered. 
        Payment shall be due within {random.randint(15, 30)} days of invoice date.<br/><br/>
        
        <b>4. CONFIDENTIALITY</b><br/>
        Both parties agree to maintain confidentiality of all proprietary information disclosed during 
        the term of this Agreement.<br/><br/>
        
        <b>5. TERMINATION</b><br/>
        Either party may terminate this Agreement with {random.randint(30, 90)} days written notice.<br/><br/>
        
        <b>6. GOVERNING LAW</b><br/>
        This Agreement shall be governed by the laws of {fake.state()}.<br/><br/>
        
        IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.<br/><br/>
        
        _____________________<br/>
        {party1}<br/><br/>
        
        _____________________<br/>
        {party2}
        """

    elif doc_type == "Non-Disclosure Agreement":
        content = f"""
        <b>NON-DISCLOSURE AGREEMENT</b><br/><br/>
        
        This Non-Disclosure Agreement ("Agreement") is entered into on {agreement_date} 
        between <b>{party1}</b> ("Disclosing Party") and <b>{party2}</b> ("Receiving Party").<br/><br/>
        
        <b>1. CONFIDENTIAL INFORMATION</b><br/>
        "Confidential Information" means any and all technical and non-technical information disclosed 
        by the Disclosing Party, including but not limited to: trade secrets, business plans, customer 
        data, financial information, and proprietary technology.<br/><br/>
        
        <b>2. OBLIGATIONS</b><br/>
        The Receiving Party agrees to:<br/>
        a) Maintain confidentiality of all Confidential Information<br/>
        b) Not disclose Confidential Information to third parties without prior written consent<br/>
        c) Use Confidential Information solely for the purpose of {fake.bs()}<br/><br/>
        
        <b>3. TERM</b><br/>
        This Agreement shall remain in effect for {random.randint(2, 5)} years from the date of execution.<br/><br/>
        
        <b>4. EXCLUSIONS</b><br/>
        This Agreement does not apply to information that: (a) is publicly available, (b) was known to 
        the Receiving Party prior to disclosure, or (c) is independently developed.<br/><br/>
        
        <b>5. RETURN OF MATERIALS</b><br/>
        Upon termination, the Receiving Party shall return or destroy all Confidential Information.<br/><br/>
        
        _____________________<br/>
        {party1}<br/><br/>
        
        _____________________<br/>
        {party2}
        """

    elif doc_type == "Compliance Certificate":
        content = f"""
        <b>COMPLIANCE CERTIFICATE</b><br/><br/>
        
        <b>Certificate Number:</b> {fake.bothify(text="COMP-####-????").upper()}<br/>
        <b>Issue Date:</b> {agreement_date}<br/>
        <b>Company Name:</b> {party1}<br/>
        <b>Company Address:</b> {fake.address().replace(chr(10), ", ")}<br/><br/>
        
        <b>CERTIFICATION</b><br/><br/>
        
        This is to certify that <b>{party1}</b> has been audited and found to be in compliance with:<br/><br/>
        
        • {random.choice(["ISO 9001:2015", "ISO 27001", "SOC 2 Type II", "GDPR", "HIPAA"])}<br/>
        • {random.choice(["PCI DSS", "CCPA", "Data Protection Act", "Financial Regulations"])}<br/>
        • Industry-specific safety and quality standards<br/><br/>
        
        <b>Audit Period:</b> {random_date(365, 180).strftime("%B %Y")} to {random_date(179, 90).strftime("%B %Y")}<br/>
        <b>Next Audit Due:</b> {random_date(89, 30).strftime("%Y-%m-%d")}<br/><br/>
        
        <b>Auditor:</b> {fake.name()}<br/>
        <b>Certification Body:</b> {fake.company()}<br/>
        <b>License Number:</b> {fake.bothify(text="LIC-######")}<br/><br/>
        
        This certificate is valid until {random_date(365, 300).strftime("%Y-%m-%d")}.<br/><br/>
        
        _____________________<br/>
        Authorized Signature
        """

    else:  # Partnership Agreement
        content = f"""
        <b>PARTNERSHIP AGREEMENT</b><br/><br/>
        
        This Partnership Agreement is made on {agreement_date} between:<br/>
        <b>Partner 1:</b> {party1}<br/>
        <b>Partner 2:</b> {party2}<br/><br/>
        
        <b>1. PARTNERSHIP NAME</b><br/>
        The partnership shall operate under the name: {fake.company()}<br/><br/>
        
        <b>2. PURPOSE</b><br/>
        The partnership is formed for the purpose of {fake.bs()} and related business activities.<br/><br/>
        
        <b>3. CAPITAL CONTRIBUTION</b><br/>
        Partner 1 shall contribute ${random.randint(50000, 500000):,}<br/>
        Partner 2 shall contribute ${random.randint(50000, 500000):,}<br/><br/>
        
        <b>4. PROFIT AND LOSS DISTRIBUTION</b><br/>
        Profits and losses shall be distributed {random.choice(["equally", "in proportion to capital contribution", "60/40", "70/30"])}.<br/><br/>
        
        <b>5. MANAGEMENT</b><br/>
        Both partners shall have equal management rights and responsibilities unless otherwise agreed in writing.<br/><br/>
        
        <b>6. DECISION MAKING</b><br/>
        Major business decisions require unanimous consent. Day-to-day operational decisions may be made individually.<br/><br/>
        
        <b>7. DISSOLUTION</b><br/>
        The partnership may be dissolved by mutual agreement or as provided by law.<br/><br/>
        
        _____________________<br/>
        {party1}<br/><br/>
        
        _____________________<br/>
        {party2}
        """

    story.append(Paragraph(content, styles["Normal"]))

    doc.build(story)
    return filename


# Generation of docs
def generate_all_documents():
    """Generate all 500 documents (100 per class)"""
    ensure_directories()

    generators = {
        "logistics": generate_logistics_document,
        "salary": generate_salary_document,
        "hr": generate_hr_document,
        "finance": generate_finance_document,
        "legal": generate_legal_document,
    }

    total_docs = 0

    for doc_class, generator_func in generators.items():
        for i in range(100):
            try:
                generator_func(i)
                total_docs += 1
            except Exception as e:
                print(f"Error generating {doc_class}_{i}: {e}")

        print(f"Completed {doc_class}: 100 documents")

    print(f"Total documents created: {total_docs}")
    print(f"Output directory: {OUTPUT_DIR}/")


if __name__ == "__main__":
    generate_all_documents()
