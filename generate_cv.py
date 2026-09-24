import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY

# Load data from data.json
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        data = json.load(f)
else:
    data = {}

p_info = data.get("personal_info", {})

# Setup Document Configuration
pdf_filename = "cv.pdf"
doc = SimpleDocTemplate(
    pdf_filename, 
    pagesize=letter, 
    rightMargin=30, 
    leftMargin=30, 
    topMargin=30, 
    bottomMargin=30
)

styles = getSampleStyleSheet()

# Color Palette
primary_color = colors.HexColor("#1E3A8A")     # Deep Blue Headers
text_dark = colors.HexColor("#1F2937")        # Main Text Charcoal
text_muted = colors.HexColor("#6B7280")       # Subtitles/Dates Gray
sidebar_bg = colors.HexColor("#F8FAFC")       # Soft light gray background for sidebar
divider_color = colors.HexColor("#E2E8F0")    # Subtle line color
body_font = "Helvetica"
bold_font = "Helvetica-Bold"

# Typography Styles
name_style = ParagraphStyle(
    'CVName', fontName=bold_font, fontSize=24, leading=28, textColor=primary_color
)
subtitle_style = ParagraphStyle(
    'CVSubtitle', fontName=body_font, fontSize=12, leading=16, textColor=text_muted, spaceAfter=8
)
body_style = ParagraphStyle(
    'CVBody', fontName=body_font, fontSize=9.5, leading=13.5, textColor=text_dark, alignment=TA_JUSTIFY
)
main_heading = ParagraphStyle(
    'CVMainHeading', fontName=bold_font, fontSize=11, leading=14, textColor=primary_color, spaceBefore=10, spaceAfter=2
)
sidebar_heading = ParagraphStyle(
    'SidebarHeading', fontName=bold_font, fontSize=10.5, leading=13, textColor=primary_color, spaceAfter=4, spaceBefore=4
)
sidebar_body = ParagraphStyle(
    'SidebarBody', fontName=body_font, fontSize=9, leading=13, textColor=text_dark
)

# Helper function to create exact full-width horizontal header dividers
def create_divider(width):
    t = Table([['']], colWidths=[width], rowHeights=[2])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1, divider_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return t

# --- BUILD LEFT COLUMN (Main Content: Name, Title, Summary, Experience) ---
left_story = []

name_text = p_info.get("name", "").strip()
title_text = p_info.get("title", "").strip()
summary_text = p_info.get("summary", "").strip()

if name_text:
    left_story.append(Paragraph(name_text, name_style))
if title_text:
    left_story.append(Paragraph(title_text, subtitle_style))

if summary_text:
    left_story.append(Paragraph(summary_text, body_style))
    left_story.append(Spacer(1, 10))

if data.get("experience"):
    left_story.append(Paragraph("WORK EXPERIENCE", main_heading))
    left_story.append(create_divider(340))
    left_story.append(Spacer(1, 6))
    
    for exp in data["experience"]:
        role = exp.get('role', '')
        company = exp.get('company', '')
        duration = exp.get('duration', '')
        
        if role or company or duration:
            formatted_duration = duration.replace(" ", "&nbsp;")
            
            exp_header_table = Table([[
                Paragraph(f"<b>{role}</b>", body_style),
                Paragraph(f"<font color='#6B7280'><b>{formatted_duration}</b></font>", ParagraphStyle('RightDate', parent=body_style, fontSize=9.5, alignment=2))
            ]], colWidths=[215, 125])
            
            exp_header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
            left_story.append(exp_header_table)
            
            if company:
                left_story.append(Paragraph(f"<font color='#6B7280'>{company}</font>", body_style))
            
            for h in exp.get("highlights", []):
                if h.strip():
                    left_story.append(Paragraph(f"&bull; {h}", body_style))
            left_story.append(Spacer(1, 6))


# --- BUILD RIGHT COLUMN (Sidebar: Contact, Skills, Education) ---
right_story = []

location = p_info.get('location', '')
phone = p_info.get('phone', '')
email = p_info.get('email', '')
linkedin = p_info.get('linkedin', '')
base_contacts = [l for l in [location, phone, email, linkedin] if l and l.strip()]
extra_contacts = [c.strip() for c in data.get("contacts", []) if c.strip()]
all_contacts = base_contacts + extra_contacts

if all_contacts:
    right_story.append(Paragraph("CONTACT", sidebar_heading))
    right_story.append(create_divider(172))
    right_story.append(Spacer(1, 4))
    
    for contact in all_contacts:
        right_story.append(Paragraph(contact, sidebar_body))
    right_story.append(Spacer(1, 10))

if data.get("skills"):
    right_story.append(Paragraph("SKILLS", sidebar_heading))
    right_story.append(create_divider(172))
    right_story.append(Spacer(1, 4))
    
    for skill in data.get("skills", []):
        if skill.strip():
            right_story.append(Paragraph(f"&bull; {skill.strip()}", sidebar_body))
    right_story.append(Spacer(1, 10))

if data.get("education"):
    right_story.append(Paragraph("EDUCATION", sidebar_heading))
    right_story.append(create_divider(172))
    right_story.append(Spacer(1, 4))
    
    for edu in data["education"]:
        degree = edu.get('degree', '')
        institution = edu.get('institution', '')
        year = edu.get('year', '')
        if degree or institution or year:
            if degree:
                right_story.append(Paragraph(f"<b>{degree}</b>", sidebar_body))
            if institution:
                right_story.append(Paragraph(f"{institution}", sidebar_body))
            if year:
                right_story.append(Paragraph(f"<font color='#6B7280'>{year}</font>", sidebar_body))
            right_story.append(Spacer(1, 4))

if not right_story:
    right_story.append(Paragraph("", sidebar_body))

# --- COMBINE INTO TWO-COLUMN TABLE LAYOUT WITH BACKGROUND & DIVIDER ---
col_widths = [355, 197]

layout_table = Table([[left_story, right_story]], colWidths=col_widths)
layout_table.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BACKGROUND', (1,0), (1,0), sidebar_bg),          
    ('LINEBEFORE', (1,0), (1,0), 1, divider_color),     
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('LEFTPADDING', (0,0), (0,0), 0),                  
    ('RIGHTPADDING', (0,0), (0,0), 15),                
    ('LEFTPADDING', (1,0), (1,0), 15),                 
    ('RIGHTPADDING', (1,0), (1,0), 10),                
]))

doc.build([layout_table])
print("cv.pdf generated successfully without profile photo!")