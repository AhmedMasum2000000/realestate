"""Generate the branded, printable moving guide."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
NAVY=colors.HexColor('#1a2b56');BURGUNDY=colors.HexColor('#862638');MUTED=colors.HexColor('#606571')
PAGE_W,PAGE_H=A4
body=ParagraphStyle('body',fontName='Helvetica',fontSize=9.5,leading=15,textColor=MUTED,spaceAfter=7)
heading=ParagraphStyle('heading',fontName='Times-Roman',fontSize=23,leading=27,textColor=NAVY,spaceBefore=16,spaceAfter=12)
title=ParagraphStyle('title',fontName='Times-Roman',fontSize=39,leading=42,textColor=NAVY,spaceAfter=15)
label=ParagraphStyle('label',fontName='Helvetica-Bold',fontSize=8,leading=12,textColor=BURGUNDY,spaceAfter=12)
sections=[
('01 / BEFORE THE FLIGHT','Build a move you understand.',[
 'Review your purpose, visa route, accepted evidence and place of application with the responsible authority.',
 'Check passport validity, insurance and arrival requirements for your own circumstances.',
 'Keep copies of important documents securely; do not put passports or bank records in an initial website enquiry.',
 'Agree a written service scope, separate official and professional fees, and cancellation terms before paid work.',
 'Prepare a monthly budget, arrival costs and a buffer. Compare actual quotes with the planning assumptions.',
 'Confirm accommodation dates, deposit, utilities, building rules and the documents needed to sign.',
 'Arrange independent legal advice before a business or property commitment.',
]),
('02 / THE FIRST WEEK','Give the everyday things a little order.',[
 'Record the permission and conditions shown for your entry; check questions with the responsible authority.',
 'Confirm your accommodation and any address-related responsibilities that apply.',
 'Set up the practical essentials: connectivity, transport and access to healthcare.',
 'Check the actual requirements for banking or other services you intend to use.',
 'Explore neighbourhoods and view properties before choosing a longer commitment.',
 'Know the name of your coordinator and who handles each next step.',
]),
('03 / YOUR FIRST MONTH','Make room to settle in.',[
 'Create a deadline calendar around your own status, reporting and renewal obligations.',
 'Review healthcare, work arrangements and tax questions with the appropriate professionals.',
 'Compare your first-month spending with your plan; revise the budget around your real routine.',
 'Check travel or re-entry arrangements before leaving Thailand.',
 'Update your plan when your employment, address, passport or family circumstances change.',
 'Agree the ongoing coordination you need and its written scope.',
]),
]

def footer(canvas,doc):
    canvas.saveState()
    canvas.setFillColor(NAVY);canvas.rect(0,PAGE_H-20*mm,PAGE_W,20*mm,fill=1,stroke=0)
    canvas.setFillColor(colors.white);canvas.setFont('Helvetica-Bold',10);canvas.drawString(20*mm,PAGE_H-12*mm,'MOVE IN THAILAND')
    canvas.setFont('Helvetica',7);canvas.drawRightString(PAGE_W-20*mm,PAGE_H-12*mm,'Visa. Home. Business. Handled.')
    canvas.setStrokeColor(colors.HexColor('#d9d9d5'));canvas.line(20*mm,20*mm,PAGE_W-20*mm,20*mm)
    canvas.setFillColor(MUTED);canvas.setFont('Helvetica',7);canvas.drawString(20*mm,14*mm,'moveinthailand.com  |  Planning guide - source check 8 October 2026')
    canvas.drawRightString(PAGE_W-20*mm,14*mm,str(doc.page));canvas.restoreState()

def main():
    output=ROOT/'mit'/'assets'/'moving-checklist.pdf';output.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=29*mm,bottomMargin=28*mm,title='Your Thailand Moving Checklist',author='Move In Thailand')
    story=[Paragraph('YOUR NEXT CHAPTER, IN ORDER',label),Paragraph('Your Thailand<br/>moving checklist.',title),Paragraph('A little clarity, before the flight and after arrival. Use this guide as a conversation starter and adapt it to your actual visa, work, family and housing circumstances.',body),Spacer(1,5*mm)]
    for section_label,section_title,items in sections:
        story.append(KeepTogether([Paragraph(section_label,label),Paragraph(section_title,heading)]))
        for item in items:
            story.append(Paragraph('&#9633; &nbsp; '+item,body))
        story.append(Spacer(1,4*mm))
    story.extend([Paragraph('Keep these questions close.',heading),Paragraph('What is included? What needs checking? Who handles it? What does it cost? What happens if my plans change?',body),Paragraph('OFFICIAL STARTING POINTS',label),Paragraph('<link href="https://www.thaievisa.go.th/">Thai e-Visa: thaievisa.go.th</link><br/><link href="https://www.immigration.go.th/">Thai Immigration Bureau: immigration.go.th</link><br/><link href="https://moveinthailand.com/visas/">Visa route guides: moveinthailand.com/visas/</link>',body),Paragraph('Authorities decide eligibility and approval. Rules and required documents can change. Specialist legal, work or tax matters need qualified advice for your circumstances.',body),Paragraph('<link href="https://moveinthailand.com/contact/">Start with a free 15-minute move conversation: moveinthailand.com/contact/</link>',body)])
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('Created the branded moving checklist PDF.')

if __name__=='__main__': main()
