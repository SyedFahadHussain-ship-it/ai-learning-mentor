from fpdf import FPDF

class PDFRoadmap(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Personalized AI Learning Roadmap', border=False, ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def create_pdf_bytes(roadmap_data: dict) -> bytes:
    pdf = PDFRoadmap()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    # Student Info
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, f"Student Name: {roadmap_data.get('student_name', 'Student')}", ln=True)
    pdf.cell(0, 8, f"Target Role: {roadmap_data.get('target_role', 'Career Goal')}", ln=True)
    pdf.ln(5)

    # Recommended Skills
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "1. Recommended Skills to Bridge Gaps", ln=True)
    pdf.set_font("Helvetica", size=11)
    for skill in roadmap_data.get('recommended_skills', []):
        pdf.cell(0, 6, f"- {skill}", ln=True)
    pdf.ln(5)

    # Weekly Plan
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "2. Weekly Study Plan", ln=True)
    for week in roadmap_data.get('weekly_plan', []):
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(0, 8, f"Week {week.get('week_number', '')}: {week.get('focus_topic', '')}", ln=True)
        pdf.set_font("Helvetica", size=10)
        for task in week.get('daily_breakdown', []):
            pdf.multi_cell(0, 5, f"  * {task}")
        pdf.ln(2)

    # Portfolio Projects
    pdf.ln(3)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "3. Suggested Portfolio Projects", ln=True)
    for proj in roadmap_data.get('suggested_projects', []):
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(0, 6, f"- {proj.get('title', '')}", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 5, f"  {proj.get('description', '')}")
        pdf.ln(2)

    # Career Tips
    pdf.ln(3)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "4. Career Tips", ln=True)
    pdf.set_font("Helvetica", size=10)
    for tip in roadmap_data.get('career_tips', []):
        pdf.multi_cell(0, 5, f"  * {tip}")

    return bytes(pdf.output()) 
