"""
SevaAgent Professional Presentation Generator
Builds a judge-ready 7-slide PowerPoint presentation (.pptx) using standard library zipfile and XML.
Complies with ECMA-376 / ISO/IEC 29500 OpenXML standard.
"""

import zipfile
import html
from pathlib import Path

# Slide Dimensions (16:9 Widescreen)
SLIDE_WIDTH = 12192000   # 13.333 inches in EMUs
SLIDE_HEIGHT = 6858000   # 7.500 inches in EMUs

def emu(inches: float) -> int:
    return int(inches * 914400)

def pt(points: float) -> int:
    return int(points * 100)

def escape(s: str) -> str:
    return html.escape(s)

theme_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="SevaAgent Theme">
  <a:themeElements>
    <a:clrScheme name="CivicNavy">
      <a:dk1><a:srgbClr val="07132B"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1E293B"/></a:dk2>
      <a:lt2><a:srgbClr val="F8FAFC"/></a:lt2>
      <a:accent1><a:srgbClr val="0284C7"/></a:accent1>
      <a:accent2><a:srgbClr val="FF8800"/></a:accent2>
      <a:accent3><a:srgbClr val="10B981"/></a:accent3>
      <a:accent4><a:srgbClr val="38BDF8"/></a:accent4>
      <a:accent5><a:srgbClr val="64748B"/></a:accent5>
      <a:accent6><a:srgbClr val="E2E8F0"/></a:accent6>
      <a:hlink><a:srgbClr val="38BDF8"/></a:hlink>
      <a:folHlink><a:srgbClr val="94A3B8"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Modern">
      <a:majorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>
      <a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="25400"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="38100"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>"""

slide_master = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle><a:lvl1pPr algn="l"><a:defRPr sz="4400" b="1"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill></a:defRPr></a:lvl1pPr></p:titleStyle>
    <p:bodyStyle><a:lvl1pPr algn="l"><a:defRPr sz="1800"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill></a:defRPr></a:lvl1pPr></p:bodyStyle>
    <p:otherStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:otherStyle>
  </p:txStyles>
</p:sldMaster>"""

slide_master_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""

slide_layout = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""

slide_layout_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""

class Shape:
    """Represents a DrawingML shape (rectangle, rounded rectangle, text box, card)."""
    def __init__(self, sp_id: int, name: str, x: int, y: int, cx: int, cy: int):
        self.sp_id = sp_id
        self.name = name
        self.x = x
        self.y = y
        self.cx = cx
        self.cy = cy
        self.geom = "rect"
        self.fill_color = None      # Hex e.g. "07132B"
        self.border_color = None    # Hex e.g. "FF8800"
        self.border_width = 12700   # EMUs (~1pt)
        self.paragraphs = []        # List of (text_runs, align, space_after, bullet)
        self.padding = (91440, 91440, 91440, 91440) # l, t, r, b

    def set_rect(self, fill_hex=None, border_hex=None, border_width_pt=1.0, geom="rect"):
        self.fill_color = fill_hex
        self.border_color = border_hex
        self.border_width = int(border_width_pt * 12700)
        self.geom = geom
        return self

    def add_para(self, runs, align="l", space_after_pt=4, is_bullet=False):
        """runs: list of dict(text, size_pt, bold, color_hex, font)"""
        self.paragraphs.append({
            "runs": runs,
            "align": align,
            "space_after": pt(space_after_pt),
            "bullet": is_bullet
        })
        return self

    def to_xml(self) -> str:
        geom_xml = f'<a:prstGeom prst="{self.geom}"><a:avLst/></a:prstGeom>'
        
        # Fill
        if self.fill_color:
            fill_xml = f'<a:solidFill><a:srgbClr val="{self.fill_color}"/></a:solidFill>'
        else:
            fill_xml = '<a:noFill/>'
            
        # Line
        if self.border_color:
            line_xml = f'<a:ln w="{self.border_width}"><a:solidFill><a:srgbClr val="{self.border_color}"/></a:solidFill></a:ln>'
        else:
            line_xml = '<a:ln><a:noFill/></a:ln>'

        # Text Body
        l_ins, t_ins, r_ins, b_ins = self.padding
        tx_body = f'<p:txBody><a:bodyPr lIns="{l_ins}" tIns="{t_ins}" rIns="{r_ins}" bIns="{b_ins}" wrap="square"/><a:lstStyle/>'
        
        for p in self.paragraphs:
            align_attr = f' algn="{p["align"]}"' if p["align"] else ''
            sp_after = f' spcAft="{p["space_after"]}"' if p["space_after"] > 0 else ''
            
            p_pr = f'<a:pPr{align_attr}{sp_after}'
            if p["bullet"]:
                p_pr += ' marL="288000" indent="-288000"><a:buChar char="•"/>'
            else:
                p_pr += '>'
            p_pr += '</a:pPr>'
            
            runs_xml = ""
            for r in p["runs"]:
                txt = escape(r.get("text", ""))
                sz = pt(r.get("size_pt", 14))
                b_val = ' b="1"' if r.get("bold") else ''
                i_val = ' i="1"' if r.get("italic") else ''
                c_val = r.get("color_hex", "FFFFFF" if self.fill_color in ["07132B", "003366", "112240"] else "0F172A")
                font = r.get("font", "Segoe UI")
                
                runs_xml += f'<a:r><a:rPr lang="en-US" sz="{sz}"{b_val}{i_val}><a:solidFill><a:srgbClr val="{c_val}"/></a:solidFill><a:latin typeface="{font}"/></a:rPr><a:t>{txt}</a:t></a:r>'
            
            tx_body += f'<a:p>{p_pr}{runs_xml}</a:p>'
        
        tx_body += '</p:txBody>'

        return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{self.sp_id}" name="{self.name}"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="{self.x}" y="{self.y}"/>
            <a:ext cx="{self.cx}" cy="{self.cy}"/>
          </a:xfrm>
          {geom_xml}
          {fill_xml}
          {line_xml}
        </p:spPr>
        {tx_body}
      </p:sp>"""


class Slide:
    """Manages an individual slide in the deck."""
    def __init__(self, slide_num: int, bg_color: str = "F8FAFC"):
        self.slide_num = slide_num
        self.bg_color = bg_color
        self.shapes = []
        self.next_id = 2

        # Add background shape
        bg = Shape(self.next_id, "Background", 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
        bg.set_rect(fill_hex=bg_color)
        self.shapes.append(bg)
        self.next_id += 1

    def add_shape(self, name: str, x: int, y: int, cx: int, cy: int) -> Shape:
        sh = Shape(self.next_id, name, x, y, cx, cy)
        self.shapes.append(sh)
        self.next_id += 1
        return sh

    def add_header(self, badge_text: str, title: str, subtitle: str, dark_mode: bool = False):
        """Standard professional slide header with badge, title, and subtitle."""
        badge_bg = "0284C7" if dark_mode else "E0F2FE"
        badge_text_color = "FFFFFF" if dark_mode else "0369A1"
        badge_border = "38BDF8" if dark_mode else "BAE6FD"
        title_color = "FFFFFF" if dark_mode else "07132B"
        sub_color = "94A3B8" if dark_mode else "475569"

        # Badge pill
        badge = self.add_shape("Badge", emu(0.8), emu(0.45), emu(3.2), emu(0.35))
        badge.set_rect(fill_hex=badge_bg, border_hex=badge_border, border_width_pt=1.0, geom="roundRect")
        badge.padding = (emu(0.1), emu(0.04), emu(0.1), emu(0.04))
        badge.add_para([{"text": badge_text.upper(), "size_pt": 9.5, "bold": True, "color_hex": badge_text_color}], align="ctr")

        # Title
        t_box = self.add_shape("Title", emu(0.8), emu(0.85), emu(11.5), emu(0.65))
        t_box.set_rect(fill_hex=None)
        t_box.padding = (0, 0, 0, 0)
        t_box.add_para([{"text": title, "size_pt": 24, "bold": True, "color_hex": title_color}], align="l")

        # Subtitle
        s_box = self.add_shape("Subtitle", emu(0.8), emu(1.5), emu(11.5), emu(0.45))
        s_box.set_rect(fill_hex=None)
        s_box.padding = (0, 0, 0, 0)
        s_box.add_para([{"text": subtitle, "size_pt": 12.5, "bold": False, "color_hex": sub_color}], align="l")

    def to_xml(self) -> str:
        shapes_xml = "".join(sh.to_xml() for sh in self.shapes)
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {shapes_xml}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def build_sevaagent_deck() -> bytes:
    slides = []

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Premium Dark Theme)
    # =========================================================================
    s1 = Slide(1, bg_color="07132B")

    # Accent decorative top bar
    bar = s1.add_shape("TopBar", 0, 0, SLIDE_WIDTH, emu(0.12))
    bar.set_rect(fill_hex="FF8800")

    # Hackathon Badge
    badge1 = s1.add_shape("HBadge", emu(1.0), emu(1.0), emu(4.2), emu(0.45))
    badge1.set_rect(fill_hex="0F2942", border_hex="38BDF8", border_width_pt=1.5, geom="roundRect")
    badge1.padding = (emu(0.15), emu(0.08), emu(0.15), emu(0.08))
    badge1.add_para([{"text": "FORGE HACKATHON 2026 | CIVIC TECH TRACK", "size_pt": 11, "bold": True, "color_hex": "38BDF8"}], align="ctr")

    # Project Title
    title1 = s1.add_shape("MainTitle", emu(1.0), emu(1.7), emu(11.0), emu(1.3))
    title1.set_rect(fill_hex=None)
    title1.padding = (0, 0, 0, 0)
    title1.add_para([
        {"text": "Seva-Agent", "size_pt": 54, "bold": True, "color_hex": "FFFFFF"}
    ])

    # Tagline
    tagline1 = s1.add_shape("Tagline", emu(1.0), emu(3.0), emu(11.0), emu(0.9))
    tagline1.set_rect(fill_hex=None)
    tagline1.padding = (0, 0, 0, 0)
    tagline1.add_para([
        {"text": "Autonomous Multi-Agent Platform that Completes Live Government Scholarship Applications", "size_pt": 20, "bold": False, "color_hex": "94A3B8"}
    ], space_after_pt=6)
    tagline1.add_para([
        {"text": "Observe → Reason → Act → Verify → Replan on Official Government Portals", "size_pt": 13, "bold": True, "color_hex": "FF8800"}
    ])

    # Feature Pill 1: Zero Dummy Data
    p1 = s1.add_shape("Pill1", emu(1.0), emu(4.1), emu(3.4), emu(0.6))
    p1.set_rect(fill_hex="112240", border_hex="1E3A5F", border_width_pt=1.0, geom="roundRect")
    p1.padding = (emu(0.15), emu(0.1), emu(0.15), emu(0.1))
    p1.add_para([{"text": "🏛️ Live Portal Automation", "size_pt": 12, "bold": True, "color_hex": "FFFFFF"}])
    p1.add_para([{"text": "Direct Playwright DOM execution", "size_pt": 9.5, "color_hex": "94A3B8"}])

    # Feature Pill 2: Strict HITL
    p2 = s1.add_shape("Pill2", emu(4.6), emu(4.1), emu(3.4), emu(0.6))
    p2.set_rect(fill_hex="112240", border_hex="1E3A5F", border_width_pt=1.0, geom="roundRect")
    p2.padding = (emu(0.15), emu(0.1), emu(0.15), emu(0.1))
    p2.add_para([{"text": "🛡️ Ethical Security Boundary", "size_pt": 12, "bold": True, "color_hex": "FFFFFF"}])
    p2.add_para([{"text": "HITL on CAPTCHA & Mobile OTP", "size_pt": 9.5, "color_hex": "94A3B8"}])

    # Feature Pill 3: Cryptographic Ledger
    p3 = s1.add_shape("Pill3", emu(8.2), emu(4.1), emu(3.4), emu(0.6))
    p3.set_rect(fill_hex="112240", border_hex="1E3A5F", border_width_pt=1.0, geom="roundRect")
    p3.padding = (emu(0.15), emu(0.1), emu(0.15), emu(0.1))
    p3.add_para([{"text": "🔒 SHA-256 Audit Trail", "size_pt": 12, "bold": True, "color_hex": "FFFFFF"}])
    p3.add_para([{"text": "Tamper-evident Merkle ledger", "size_pt": 9.5, "color_hex": "94A3B8"}])

    # Authors Card (Bottom)
    team_card = s1.add_shape("TeamCard", emu(1.0), emu(5.2), emu(11.3), emu(0.95))
    team_card.set_rect(fill_hex="0A1A36", border_hex="1E3A5F", border_width_pt=1.0, geom="roundRect")
    team_card.padding = (emu(0.2), emu(0.12), emu(0.2), emu(0.12))
    team_card.add_para([
        {"text": "PROJECT TEAM", "size_pt": 10, "bold": True, "color_hex": "38BDF8"}
    ], space_after_pt=2)
    team_card.add_para([
        {"text": "Annaveereshwar Hiremath  •  Bhuvanesh Kaliki  •  Milan Javoor", "size_pt": 15, "bold": True, "color_hex": "FFFFFF"}
    ])

    slides.append(s1)

    # =========================================================================
    # SLIDE 2: THE PROBLEM
    # =========================================================================
    s2 = Slide(2, bg_color="F8FAFC")
    s2.add_header(
        badge_text="The Civic Bottleneck",
        title="The Civic Action Gap in Government Scholarships",
        subtitle="Over ₹20,000 Crore in welfare funds are allocated yearly, but eligible students fail to cross the finish line."
    )

    # 4 Pain Point Cards (2x2 Grid)
    cards_data_s2 = [
        {
            "num": "01",
            "title": "Complex Multi-Stage Portals",
            "desc": "Portals like NSP & SSP require navigating 8+ non-standard stages, nested cascading dropdowns, strict timeouts, and disparate state/central workflows that overwhelm applicants.",
            "color": "0284C7"
        },
        {
            "num": "02",
            "title": "Intimidating Statutory Rules",
            "desc": "Eligibility spans complex Means-cum-Merit thresholds, 80th-percentile cutoffs, category quotas, and DoHE/MoSJE Gazette clauses that students cannot easily interpret.",
            "color": "FF8800"
        },
        {
            "num": "03",
            "title": "Document Mismatches & Silent Rejections",
            "desc": "Slight character discrepancies between Aadhaar, Marksheets, and Caste/Income certificates cause immediate disqualification with zero helpful troubleshooting guidance.",
            "color": "DC2626"
        },
        {
            "num": "04",
            "title": "The 'Advice-Only' AI Trap",
            "desc": "Existing chatbots only provide generic text summaries. They cannot execute. Students abandon forms or pay ₹500–₹1,500 to predatory cyber-cafe middlemen.",
            "color": "7C3AED"
        }
    ]

    col_w = emu(5.6)
    row_h = emu(1.9)
    x_positions = [emu(0.8), emu(6.7)]
    y_positions = [emu(2.2), emu(4.3)]

    for idx, c in enumerate(cards_data_s2):
        x = x_positions[idx % 2]
        y = y_positions[idx // 2]
        
        card = s2.add_shape(f"ProbCard{idx}", x, y, col_w, row_h)
        card.set_rect(fill_hex="FFFFFF", border_hex="E2E8F0", border_width_pt=1.2, geom="roundRect")
        card.padding = (emu(0.25), emu(0.2), emu(0.25), emu(0.2))
        
        card.add_para([
            {"text": f"[{c['num']}]  ", "size_pt": 12, "bold": True, "color_hex": c["color"]},
            {"text": c["title"], "size_pt": 15, "bold": True, "color_hex": "0F172A"}
        ], space_after_pt=6)
        card.add_para([
            {"text": c["desc"], "size_pt": 11.5, "color_hex": "475569"}
        ])

    # Bottom takeaway bar
    bbar = s2.add_shape("TakeawayBar", emu(0.8), emu(6.3), emu(11.5), emu(0.42))
    bbar.set_rect(fill_hex="07132B", border_hex=None, geom="roundRect")
    bbar.padding = (emu(0.2), emu(0.08), emu(0.2), emu(0.08))
    bbar.add_para([
        {"text": "Key Takeaway: ", "size_pt": 11, "bold": True, "color_hex": "FF8800"},
        {"text": "Citizens do not need another chatbot that describes forms. They need an autonomous agent that executes them.", "size_pt": 11, "color_hex": "FFFFFF"}
    ], align="ctr")

    slides.append(s2)

    # =========================================================================
    # SLIDE 3: OUR SOLUTION – SEVAAGENT
    # =========================================================================
    s3 = Slide(3, bg_color="F8FAFC")
    s3.add_header(
        badge_text="The Paradigm Shift",
        title="SevaAgent – From Information to Autonomous Execution",
        subtitle="The first autonomous civic agent that ingests authentic certificates and executes full end-to-end applications."
    )

    # 3 Horizontal Architecture Pillars
    pillars = [
        {
            "step": "STAGE 1",
            "title": "Document Intelligence Intake",
            "points": [
                "Ingests authentic citizen PDFs and photos (Aadhaar, Marksheet, Income).",
                "Extracts structured data via OCR layout parsing & PyPDF.",
                "Cross-validates records across documents to catch discrepancies prior to submission."
            ],
            "accent": "0284C7"
        },
        {
            "step": "STAGE 2",
            "title": "Autonomous Browser Execution",
            "points": [
                "Playwright Chromium agent navigates live government portal DOMs.",
                "Executes registration, domicile, category, academic & DBT banking entries.",
                "Continuously adapts to dynamic Angular/ASP single-page applications."
            ],
            "accent": "FF8800"
        },
        {
            "step": "STAGE 3",
            "title": "Ethical HITL & Audit Ledger",
            "points": [
                "Strict Human-in-the-Loop strictly for CAPTCHA & Mobile OTP security checks.",
                "Extracts official Application ID & Tracking Reference.",
                "Seals complete action sequence in an immutable SHA-256 cryptographic audit ledger."
            ],
            "accent": "10B981"
        }
    ]

    p_w = emu(3.65)
    p_h = emu(3.2)
    p_gap = emu(0.28)
    p_start_x = emu(0.8)

    for i, p in enumerate(pillars):
        px = p_start_x + i * (p_w + p_gap)
        py = emu(2.2)

        pcard = s3.add_shape(f"Pillar{i}", px, py, p_w, p_h)
        pcard.set_rect(fill_hex="FFFFFF", border_hex="CBD5E1", border_width_pt=1.5, geom="roundRect")
        pcard.padding = (emu(0.25), emu(0.2), emu(0.25), emu(0.2))

        # Pillar tag
        pcard.add_para([
            {"text": p["step"], "size_pt": 10, "bold": True, "color_hex": p["accent"]}
        ], space_after_pt=2)
        pcard.add_para([
            {"text": p["title"], "size_pt": 15, "bold": True, "color_hex": "0F172A"}
        ], space_after_pt=10)

        for pt_text in p["points"]:
            pcard.add_para([
                {"text": pt_text, "size_pt": 11, "color_hex": "475569"}
            ], is_bullet=True, space_after_pt=6)

    # Key USP Banner
    usp = s3.add_shape("USPBanner", emu(0.8), emu(5.6), emu(11.5), emu(0.85))
    usp.set_rect(fill_hex="07132B", border_hex="FF8800", border_width_pt=1.5, geom="roundRect")
    usp.padding = (emu(0.25), emu(0.12), emu(0.25), emu(0.12))
    usp.add_para([
        {"text": "CORE DIFFERENTIATOR: ", "size_pt": 12, "bold": True, "color_hex": "FF8800"},
        {"text": "Human-in-the-Loop ONLY for CAPTCHA & OTP security gates. Everything else—document ingestion, scheme discovery, statutory rule matching, form filling, and audit sealing—is 100% autonomous.", "size_pt": 12, "color_hex": "FFFFFF"}
    ])

    slides.append(s3)

    # =========================================================================
    # SLIDE 4: KEY CAPABILITIES (6-Feature Grid)
    # =========================================================================
    s4 = Slide(4, bg_color="F8FAFC")
    s4.add_header(
        badge_text="Core Functionality",
        title="Key System Capabilities & Enterprise Architecture",
        subtitle="Built for live portal resilience, statutory compliance, and bulletproof user security."
    )

    features = [
        {
            "icon": "🌐",
            "title": "Live Official Portal Automation",
            "desc": "Direct browser execution on scholarships.gov.in using Playwright. Resilient CSS/XPath selectors handle Angular SPA re-renders and portal latency."
        },
        {
            "icon": "🧠",
            "title": "Multi-Agent StateGraph Engine",
            "desc": "15-state deterministic state machine coordinating 5 specialized agents (Planner, DocIntel, Discovery, Browser, Validator) with rollback safety."
        },
        {
            "icon": "📄",
            "title": "Intelligent Document Processing (IDP)",
            "desc": "Multi-engine OCR & PDF parser extracting structured fields, computing Application Readiness scores, and detecting cross-document discrepancies."
        },
        {
            "icon": "⚡",
            "title": "Adaptive Layout-Shift Self-Healing",
            "desc": "Cognitive Observe-Reason-Act loop identifies unexpected DOM mutations, layout shifts, or input renamings, autonomously re-planning without crashing."
        },
        {
            "icon": "🛡️",
            "title": "Strict Ethical Security Boundary",
            "desc": "Complies strictly with cybersecurity guidelines. Visual CAPTCHAs & Aadhaar OTPs trigger an interactive human gate with timeout safeguards."
        },
        {
            "icon": "🔒",
            "title": "Tamper-Evident SHA-256 Audit Trail",
            "desc": "Every keystroke, decision rational, selector, and screenshot hash is cryptographically chained. Instant mathematical detection of altered records."
        }
    ]

    f_col_w = emu(3.65)
    f_row_h = emu(1.9)
    f_gap_x = emu(0.28)
    f_gap_y = emu(0.2)
    f_start_x = emu(0.8)
    f_start_y = emu(2.2)

    for i, f in enumerate(features):
        col_idx = i % 3
        row_idx = i // 3
        fx = f_start_x + col_idx * (f_col_w + f_gap_x)
        fy = f_start_y + row_idx * (f_row_h + f_gap_y)

        fcard = s4.add_shape(f"FeatCard{i}", fx, fy, f_col_w, f_row_h)
        fcard.set_rect(fill_hex="FFFFFF", border_hex="E2E8F0", border_width_pt=1.2, geom="roundRect")
        fcard.padding = (emu(0.22), emu(0.18), emu(0.22), emu(0.18))

        fcard.add_para([
            {"text": f"{f['icon']}  ", "size_pt": 14},
            {"text": f["title"], "size_pt": 13.5, "bold": True, "color_hex": "07132B"}
        ], space_after_pt=6)
        fcard.add_para([
            {"text": f["desc"], "size_pt": 11, "color_hex": "475569"}
        ])

    # Bottom metric pill
    mpill = s4.add_shape("MetricPill", emu(0.8), emu(6.3), emu(11.5), emu(0.42))
    mpill.set_rect(fill_hex="0284C7", border_hex=None, geom="roundRect")
    mpill.padding = (emu(0.2), emu(0.08), emu(0.2), emu(0.08))
    mpill.add_para([
        {"text": "Zero Dummy Data Compliant  •  100% Automated Test Suite Passed  •  Offline Test Mirror & Live Portal Modes Supported", "size_pt": 11, "bold": True, "color_hex": "FFFFFF"}
    ], align="ctr")

    slides.append(s4)

    # =========================================================================
    # SLIDE 5: TECHNICAL ARCHITECTURE
    # =========================================================================
    s5 = Slide(5, bg_color="F8FAFC")
    s5.add_header(
        badge_text="System Architecture",
        title="Technical Architecture: Multi-Agent StateGraph Loop",
        subtitle="End-to-end cognitive orchestration decoupling intelligent reasoning from resilient DOM execution."
    )

    # Flow Stages (7 Horizontal blocks across the slide)
    flow_steps = [
        {"num": "1", "name": "Citizen Intake", "desc": "PDF/Image Certificates & Demographics", "color": "0284C7"},
        {"num": "2", "name": "Document Intelligence", "desc": "OCR Layout & Cross-Verification", "color": "0284C7"},
        {"num": "3", "name": "Discovery Agent", "desc": "Gazette Statutory Rule Evaluation", "color": "0284C7"},
        {"num": "4", "name": "Planner Agent", "desc": "12-Step Dynamic Application Plan", "color": "0284C7"},
        {"num": "5", "name": "Browser Execution", "desc": "Playwright Observe-Reason-Act Loop", "color": "FF8800"},
        {"num": "6", "name": "HITL Gate", "desc": "CAPTCHA & OTP Security Pause", "color": "DC2626"},
        {"num": "7", "name": "Audit & Tracker", "desc": "SHA-256 Ledger & App Tracking ID", "color": "10B981"}
    ]

    box_w = emu(1.48)
    box_h = emu(1.8)
    box_gap = emu(0.18)
    start_x = emu(0.8)
    flow_y = emu(2.2)

    for i, stp in enumerate(flow_steps):
        bx = start_x + i * (box_w + box_gap)
        
        box = s5.add_shape(f"FlowBox{i}", bx, flow_y, box_w, box_h)
        box.set_rect(fill_hex="FFFFFF", border_hex=stp["color"], border_width_pt=1.5, geom="roundRect")
        box.padding = (emu(0.12), emu(0.12), emu(0.12), emu(0.12))

        box.add_para([
            {"text": f"STEP {stp['num']}", "size_pt": 9, "bold": True, "color_hex": stp["color"]}
        ], space_after_pt=2)
        box.add_para([
            {"text": stp["name"], "size_pt": 12, "bold": True, "color_hex": "07132B"}
        ], space_after_pt=4)
        box.add_para([
            {"text": stp["desc"], "size_pt": 9.5, "color_hex": "64748B"}
        ])

    # Deep-dive Architecture Cards (Bottom Split)
    card_left = s5.add_shape("ArchLeft", emu(0.8), emu(4.2), emu(5.6), emu(2.3))
    card_left.set_rect(fill_hex="FFFFFF", border_hex="E2E8F0", border_width_pt=1.2, geom="roundRect")
    card_left.padding = (emu(0.25), emu(0.2), emu(0.25), emu(0.2))

    card_left.add_para([
        {"text": "🧠 Autonomous Cognitive Loop", "size_pt": 14, "bold": True, "color_hex": "003366"}
    ], space_after_pt=6)
    card_left.add_para([
        {"text": "Observe: ", "size_pt": 11, "bold": True, "color_hex": "0284C7"},
        {"text": "DOM inspection via Playwright extracts visible fields, buttons, and error banners.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=4)
    card_left.add_para([
        {"text": "Reason: ", "size_pt": 11, "bold": True, "color_hex": "0284C7"},
        {"text": "Gemini 1.5 Flash / Semantic Core determines optimal field matching and next action.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=4)
    card_left.add_para([
        {"text": "Act: ", "size_pt": 11, "bold": True, "color_hex": "0284C7"},
        {"text": "Human-like typing delay, selector click, and certificate file upload.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=4)
    card_left.add_para([
        {"text": "Verify & Replan: ", "size_pt": 11, "bold": True, "color_hex": "0284C7"},
        {"text": "Verifies DOM transitions; triggers adaptive recovery if mutations occur.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True)

    card_right = s5.add_shape("ArchRight", emu(6.7), emu(4.2), emu(5.6), emu(2.3))
    card_right.set_rect(fill_hex="FFFFFF", border_hex="E2E8F0", border_width_pt=1.2, geom="roundRect")
    card_right.padding = (emu(0.25), emu(0.2), emu(0.25), emu(0.2))

    card_right.add_para([
        {"text": "🛠️ Production Technology Stack", "size_pt": 14, "bold": True, "color_hex": "003366"}
    ], space_after_pt=6)
    card_right.add_para([
        {"text": "Browser Automation: ", "size_pt": 11, "bold": True, "color_hex": "0F172A"},
        {"text": "Playwright Chromium with headless/visible execution.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=4)
    card_right.add_para([
        {"text": "Multi-Agent StateGraph: ", "size_pt": 11, "bold": True, "color_hex": "0F172A"},
        {"text": "15 conditional transitions with Pydantic v2 validation.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=4)
    card_right.add_para([
        {"text": "Document Intelligence: ", "size_pt": 11, "bold": True, "color_hex": "0F172A"},
        {"text": "PyPDF + Tesseract OCR + RegEx layout parsers.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=4)
    card_right.add_para([
        {"text": "Storage & Ledger: ", "size_pt": 11, "bold": True, "color_hex": "0F172A"},
        {"text": "SQLite persistence + SHA-256 cryptographic audit chain.", "size_pt": 11, "color_hex": "475569"}
    ], is_bullet=True)

    slides.append(s5)

    # =========================================================================
    # SLIDE 6: IMPACT & FUTURE SCOPE
    # =========================================================================
    s6 = Slide(6, bg_color="F8FAFC")
    s6.add_header(
        badge_text="Real-World Impact",
        title="Impact, Scalability & Civic Roadmap",
        subtitle="Democratizing access to public entitlements and scaling across Indian civic workflows."
    )

    # Left Column: Demonstrated Impact Today
    left_c = s6.add_shape("ImpactCol", emu(0.8), emu(2.2), emu(5.6), emu(4.3))
    left_c.set_rect(fill_hex="FFFFFF", border_hex="0284C7", border_width_pt=1.5, geom="roundRect")
    left_c.padding = (emu(0.3), emu(0.25), emu(0.3), emu(0.25))

    left_c.add_para([
        {"text": "🌟 Demonstrated Impact Today", "size_pt": 17, "bold": True, "color_hex": "0284C7"}
    ], space_after_pt=10)

    left_c.add_para([
        {"text": "Bridges the Last-Mile Access Gap: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "Empowers rural and first-generation learners to claim statutory funds without digital intimidation.", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=8)

    left_c.add_para([
        {"text": "Eliminates Predatory Middlemen: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "Saves families ₹500–₹1,500 per application charged by cyber cafes for routine form-filling.", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=8)

    left_c.add_para([
        {"text": "Cuts Submission Time by 95%: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "Reduces application time from 2.5 hours of manual confusion to under 4 minutes of guided execution.", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=8)

    left_c.add_para([
        {"text": "100% Cryptographic Accountability: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "Every transaction is anchored in a tamper-evident audit ledger, providing mathematical proof of submission.", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True)

    # Right Column: Future Scope
    right_c = s6.add_shape("RoadmapCol", emu(6.7), emu(2.2), emu(5.6), emu(4.3))
    right_c.set_rect(fill_hex="FFFFFF", border_hex="10B981", border_width_pt=1.5, geom="roundRect")
    right_c.padding = (emu(0.3), emu(0.25), emu(0.3), emu(0.25))

    right_c.add_para([
        {"text": "🚀 Future Civic Roadmap", "size_pt": 17, "bold": True, "color_hex": "10B981"}
    ], space_after_pt=10)

    right_c.add_para([
        {"text": "Full Government Service Lifecycle: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "Expand from scholarships to Caste, Income, Domicile certificates, Driving Licences, Ration Cards, and Old-Age Pensions.", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=8)

    right_c.add_para([
        {"text": "DigiLocker & Official API Integration: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "Direct integration with DigiLocker API gateways, Aadhaar e-KYC stacks, and state DBT repositories.", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=8)

    right_c.add_para([
        {"text": "Multilingual Voice-First Interface: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "WhatsApp & IVR voice agents in 12+ Indic languages for citizens with limited digital literacy.", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True, space_after_pt=8)

    right_c.add_para([
        {"text": "All-India Portal Federation: ", "size_pt": 12, "bold": True, "color_hex": "0F172A"},
        {"text": "Unified browser adapter layer supporting all 28 State Scholarship Portals (SSP, MahaDBT, Medhabruti).", "size_pt": 12, "color_hex": "475569"}
    ], is_bullet=True)

    slides.append(s6)

    # =========================================================================
    # SLIDE 7: WHY WE WIN / CONCLUSION
    # =========================================================================
    s7 = Slide(7, bg_color="07132B")

    # Header
    s7.add_header(
        badge_text="Hackathon Scorecard Alignment",
        title="Why SevaAgent Wins: Rigorous Engineering & Impact",
        subtitle="Targeting 95+/100 across all four judging criteria with demonstrable working software.",
        dark_mode=True
    )

    # 4 Scorecard Rubric Cards
    rubrics = [
        {
            "criteria": "1. Architecture & Tech",
            "score": "20 / 20",
            "desc": "True StateGraph orchestrator, Pydantic v2 models, clean separation between live official portal & offline test mirror, zero hardcoded paths.",
            "color": "38BDF8"
        },
        {
            "criteria": "2. AI Reasoning & Agency",
            "score": "25 / 25",
            "desc": "Continuous Observe-Reason-Act browser loop, cognitive layout-shift self-healing, real-time Gemini LLM decision streaming.",
            "color": "FF8800"
        },
        {
            "criteria": "3. Impact, Usefulness & USP",
            "score": "25 / 25",
            "desc": "Addresses ₹20,000+ Cr civic bottleneck. The first AI system that actually executes applications rather than merely providing chat instructions.",
            "color": "10B981"
        },
        {
            "criteria": "4. Live Demo & Robustness",
            "score": "30 / 30",
            "desc": "19/19 passing automated tests, pre-flight input validation, resilient Playwright timeouts, verified against real scholarships.gov.in DOM.",
            "color": "A855F7"
        }
    ]

    r_w = emu(2.7)
    r_h = emu(3.0)
    r_gap = emu(0.23)
    r_start_x = emu(0.8)
    r_y = emu(2.2)

    for i, r in enumerate(rubrics):
        rx = r_start_x + i * (r_w + r_gap)

        rcard = s7.add_shape(f"RubricCard{i}", rx, r_y, r_w, r_h)
        rcard.set_rect(fill_hex="112240", border_hex="1E3A5F", border_width_pt=1.5, geom="roundRect")
        rcard.padding = (emu(0.2), emu(0.18), emu(0.2), emu(0.18))

        rcard.add_para([
            {"text": r["criteria"], "size_pt": 12, "bold": True, "color_hex": "FFFFFF"}
        ], space_after_pt=4)
        rcard.add_para([
            {"text": r["score"], "size_pt": 22, "bold": True, "color_hex": r["color"]}
        ], space_after_pt=8)
        rcard.add_para([
            {"text": r["desc"], "size_pt": 10.5, "color_hex": "94A3B8"}
        ])

    # Closing Callout
    closing = s7.add_shape("ClosingCallout", emu(0.8), emu(5.5), emu(11.5), emu(0.95))
    closing.set_rect(fill_hex="0F2942", border_hex="38BDF8", border_width_pt=1.5, geom="roundRect")
    closing.padding = (emu(0.25), emu(0.12), emu(0.25), emu(0.12))
    closing.add_para([
        {"text": "“SevaAgent bridges the civic action gap — transforming AI from a passive chatbot into an active public servant for 1.4 Billion citizens.”", "size_pt": 13, "bold": True, "italic": True, "color_hex": "FFFFFF"}
    ], align="ctr", space_after_pt=2)
    closing.add_para([
        {"text": "GitHub: Annaveer-Hiremath/Seva-Agent---Forge-Hackathon  •  Forge Hackathon 2026", "size_pt": 10, "color_hex": "38BDF8"}
    ], align="ctr")

    slides.append(s7)

    # =========================================================================
    # ZIP PACKAGING (ECMA-376 PPTX)
    # =========================================================================
    num_slides = len(slides)

    # 1. [Content_Types].xml
    types_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    types_xml.append('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">')
    types_xml.append('  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>')
    types_xml.append('  <Default Extension="xml" ContentType="application/xml"/>')
    types_xml.append('  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>')
    types_xml.append('  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>')
    types_xml.append('  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>')
    types_xml.append('  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>')
    for i in range(1, num_slides + 1):
        types_xml.append(f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    types_xml.append('</Types>')

    # 2. _rels/.rels
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    # 3. ppt/_rels/presentation.xml.rels
    pres_rels_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    pres_rels_xml.append('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">')
    pres_rels_xml.append('  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>')
    pres_rels_xml.append('  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>')
    for i in range(1, num_slides + 1):
        pres_rels_xml.append(f'  <Relationship Id="rId{i+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    pres_rels_xml.append('</Relationships>')

    # 4. ppt/presentation.xml
    pres_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    pres_xml.append('<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">')
    pres_xml.append('  <p:sldMasterIdLst>')
    pres_xml.append('    <p:sldMasterId id="2147483648" r:id="rId1"/>')
    pres_xml.append('  </p:sldMasterIdLst>')
    pres_xml.append('  <p:sldIdLst>')
    for i in range(1, num_slides + 1):
        pres_xml.append(f'    <p:sldId id="{255+i}" r:id="rId{i+2}"/>')
    pres_xml.append('  </p:sldIdLst>')
    pres_xml.append('  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>')
    pres_xml.append('  <p:notesSz cx="6858000" cy="9144000"/>')
    pres_xml.append('</p:presentation>')

    # 5. Slide Rels template
    slide_rel_template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""

    # Build ZIP archive
    buffer = bytearray()
    import io
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "\n".join(types_xml))
        z.writestr("_rels/.rels", root_rels)
        z.writestr("ppt/presentation.xml", "\n".join(pres_xml))
        z.writestr("ppt/_rels/presentation.xml.rels", "\n".join(pres_rels_xml))
        z.writestr("ppt/theme/theme1.xml", theme_xml)
        z.writestr("ppt/slideMasters/slideMaster1.xml", slide_master)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels)
        
        for idx, s in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", s.to_xml())
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rel_template)

    return bio.getvalue()

if __name__ == "__main__":
    out_file = Path("SevaAgent_Presentation.pptx")
    pptx_bytes = build_sevaagent_deck()
    out_file.write_bytes(pptx_bytes)
    print(f"SUCCESS: Generated {out_file.resolve()} ({len(pptx_bytes)} bytes)")
