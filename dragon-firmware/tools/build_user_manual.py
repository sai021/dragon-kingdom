"""Build the printable end-user manual from docs/USER-MANUAL.md."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'output/pdf/dragon-kingdom-user-manual.pdf'
PURPLE=colors.HexColor('#34304e')
TEAL=colors.HexColor('#236a70')

def inline(text):
    text=re.sub('[\u2010-\u2015\u2212]','-',text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',escape(text))
    return re.sub(r'https?://[^\s<>]+',lambda m: '<link href="'+m[0]+'" color="#236a70">'+m[0]+'</link>',text)

class NumberedCanvas(Canvas):
    """Add the actual total after layout, including any overflow pages."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.states=[]
    def showPage(self):
        self.states.append(dict(self.__dict__));self._startPage()
    def save(self):
        total=len(self.states)
        for state in self.states:
            self.__dict__.update(state)
            self.setFont('Helvetica',8);self.setFillColor(colors.HexColor('#686574'))
            self.drawRightString(A4[0]-52,28,f'{self._pageNumber} / {total}')
            super().showPage()
        super().save()

def build():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    source=(ROOT/'docs/USER-MANUAL.md').read_text(encoding='utf-8')
    edition=re.search(r'version ([0-9.]+),\s+(\d+ [A-Za-z]+ \d{4})',source)
    if not edition:raise ValueError('Manual must include its version and edition date.')
    version,date=edition.groups()
    chunks=source.split('<!-- page -->')
    styles={
      'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=30,leading=35,textColor=PURPLE,spaceAfter=10),
      'subtitle':ParagraphStyle('subtitle',fontName='Helvetica',fontSize=13,leading=18,textColor=TEAL,spaceAfter=24),
      'heading':ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=15,leading=19,textColor=PURPLE,spaceBefore=15,spaceAfter=9,keepWithNext=True),
      'body':ParagraphStyle('body',fontName='Helvetica',fontSize=11.7,leading=16.4,textColor=colors.HexColor('#34343e'),spaceAfter=11),
      'list':ParagraphStyle('list',fontName='Helvetica',fontSize=11.7,leading=16.4,textColor=colors.HexColor('#34343e'),leftIndent=20,firstLineIndent=0,bulletIndent=1,spaceAfter=9),
    }
    def decoration(canvas,doc):
        width,height=A4;canvas.saveState()
        canvas.setFillColor(TEAL);canvas.rect(0,height-9,width,9,fill=1,stroke=0)
        canvas.setFont('Helvetica-Bold',9);canvas.setFillColor(PURPLE);canvas.drawString(52,height-35,'DRAGON KINGDOM  /  USER MANUAL')
        canvas.setStrokeColor(colors.HexColor('#dddbe6'));canvas.line(52,42,width-52,42)
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#686574'))
        canvas.drawString(52,28,f'Shipping edition {version}  |  {date}');canvas.restoreState()
    story=[]
    for page_index,chunk in enumerate(chunks):
        if page_index:story.append(PageBreak())
        lines=chunk.strip().splitlines();i=0;subtitle=True
        while i<len(lines):
            line=lines[i].strip()
            if not line:i+=1;continue
            if line.startswith('[QR: ') and line.endswith(']'):
                widget=QrCodeWidget(line[5:-1]);x0,y0,x1,y1=widget.getBounds();size=76
                drawing=Drawing(size,size,transform=[size/(x1-x0),0,0,size/(y1-y0),0,0]);drawing.add(widget)
                story.extend([drawing,Spacer(1,6)]);i+=1;continue
            if line.startswith('# '):story.append(Paragraph(inline(line[2:]),styles['title']));i+=1;continue
            if line.startswith('## '):story.append(Paragraph(inline(line[3:]),styles['heading']));subtitle=False;i+=1;continue
            match=re.match(r'^(\d+)\.\s+(.+)|^-\s+(.+)',line)
            if match:
                text=match.group(2) or match.group(3);bullet=(match.group(1)+'.') if match.group(1) else '\u2022';i+=1
                while i<len(lines) and lines[i].strip() and not re.match(r'^(?:\d+\.|-|#)\s',lines[i].strip()):text+=' '+lines[i].strip();i+=1
                story.append(Paragraph(inline(text),styles['list'],bulletText=bullet));continue
            text=line;i+=1
            while i<len(lines) and lines[i].strip() and not re.match(r'^(?:\d+\.|-|#)\s',lines[i].strip()):text+=' '+lines[i].strip();i+=1
            story.append(Paragraph(inline(text),styles['subtitle'] if subtitle else styles['body']));subtitle=False
    doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=52,leftMargin=52,topMargin=62,bottomMargin=58,title='Dragon Kingdom - User Manual',author='Dragon Kingdom',subject='Touch controls, phone setup, collections, custom dragons and sunrise alarm')
    doc.build(story,onFirstPage=decoration,onLaterPages=decoration,canvasmaker=NumberedCanvas)
    print(OUTPUT)

if __name__=='__main__':build()
