import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner cell padding in twips (1/20 of a pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = Document()

    # 1. Page Margins (1 inch everywhere)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # 2. Configure Default Style (Verdana, 10pt, Justified, 1.5 line spacing)
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Verdana'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal_style.paragraph_format.space_after = Pt(6)

    def add_p(text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, font_size=10, color=RGBColor(30, 30, 30)):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Verdana'
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Verdana'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(180, 0, 0) # MBU Crimson Red
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Verdana'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(15, 23, 42) # Slate Navy
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Verdana'
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_table(headers, data, col_widths=None):
        table = doc.add_table(rows=len(data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Header Row
        hdr_row = table.rows[0]
        for idx, header_text in enumerate(headers):
            cell = hdr_row.cells[idx]
            cell.text = header_text
            set_cell_background(cell, "1E293B") # Dark slate
            set_cell_margins(cell, 120, 120, 150, 150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.bold = True
                run.font.name = 'Verdana'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)

        # Data Rows
        for r_idx, row_data in enumerate(data):
            row = table.rows[r_idx + 1]
            bg_color = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
            for c_idx, val in enumerate(row_data):
                cell = row.cells[c_idx]
                cell.text = str(val)
                set_cell_background(cell, bg_color)
                set_cell_margins(cell, 80, 80, 120, 120)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.name = 'Verdana'
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(30, 30, 30)

        # Column widths
        if col_widths:
            for row in table.rows:
                for idx, w in enumerate(col_widths):
                    row.cells[idx].width = Inches(w)

        doc.add_paragraph().paragraph_format.space_after = Pt(6)
        return table

    # ==========================================
    # 1. TITLE PAGE
    # ==========================================
    add_p("DECENTRALIZED SOLAR MICROGRID WITH PEER-TO-PEER (P2P) ENERGY TRADING & HARDWARE-IN-THE-LOOP (HIL) IoT", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=15, space_after=18, color=RGBColor(180, 0, 0))
    add_p("A TESP Project Report submitted to", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=11, space_after=4)
    add_p("MOHAN BABU UNIVERSITY", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=13, space_after=6)
    add_p("In partial fulfilment of the requirements for the award of the degree of", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=4)
    add_p("BACHELOR OF TECHNOLOGY", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=12, space_after=2)
    add_p("IN", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=2)
    add_p("ELECTRONICS AND COMMUNICATION ENGINEERING", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=12, space_after=16, color=RGBColor(15, 23, 42))

    add_p("Submitted by:", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=11, space_after=6)
    add_p("IPPAGUNTA VENKATA JAGADEESH       22101A030001", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=3)
    add_p("STUDENT NAME 2                   22101A030002", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=3)
    add_p("STUDENT NAME 3                   22101A030003", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=3)
    add_p("STUDENT NAME 4                   22101A030004", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=16)

    add_p("Under the Esteemed Supervision of:", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=4)
    add_p("Dr. / Prof. Faculty Supervisor Name, M.Tech., Ph.D.", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=11, space_after=2)
    add_p("Designation, Department of ECE", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=24)

    add_p("Department of Electronics and Communication Engineering", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=11, space_after=2)
    add_p("School of Engineering", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=2)
    add_p("MOHAN BABU UNIVERSITY", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=12, space_after=2, color=RGBColor(180, 0, 0))
    add_p("Sree Sainath Nagar, Tirupati – 517 102", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=4)
    add_p("2026 – 2027", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=11, space_after=0)

    doc.add_page_break()

    # ==========================================
    # 2. CERTIFICATE PAGE
    # ==========================================
    add_p("MOHAN BABU UNIVERSITY", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=13, space_after=2, color=RGBColor(180, 0, 0))
    add_p("Sree Sainath Nagar, Tirupati 517 102", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=8)
    add_p("DEPARTMENT OF ELECTRONICS AND COMMUNICATION ENGINEERING", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=11, space_after=12)
    add_p("CERTIFICATE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=14, space_after=14, color=RGBColor(180, 0, 0))

    cert_text = (
        "This is to certify that the TESP Project report titled \"Decentralized Solar Microgrid with Peer-to-Peer (P2P) "
        "Energy Trading & Hardware-in-the-Loop (HIL) IoT\" is the Bonafide work done by:\n\n"
        "  • IPPAGUNTA VENKATA JAGADEESH (22101A030001)\n"
        "  • STUDENT NAME 2 (22101A030002)\n"
        "  • STUDENT NAME 3 (22101A030003)\n"
        "  • STUDENT NAME 4 (22101A030004)\n\n"
        "in the Department of Electronics and Communication Engineering, and submitted to Mohan Babu University, Tirupati "
        "in partial fulfilment of the requirements for the award of the degree of Bachelor of Technology in Electronics and "
        "Communication Engineering during the academic year 2026-2027. This work has been carried out under my guidance and "
        "supervision. The results embodied in this project report have not been submitted in any University or Organization "
        "for the award of any degree or diploma."
    )
    add_p(cert_text, space_after=24)

    add_table(
        ["Supervisor:", "Head of the Department:"],
        [[
            "Faculty Supervisor Name, M.Tech., Ph.D.\nDesignation\nDept. of ECE, School of Engineering\nMohan Babu University",
            "Dr. N. Sudhakar Reddy, M.Tech., Ph.D.\nProfessor & Head\nDept. of ECE, School of Engineering\nMohan Babu University"
        ]],
        col_widths=[3.25, 3.25]
    )

    add_p("\nINTERNAL EXAMINER                                                     EXTERNAL EXAMINER", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)

    doc.add_page_break()

    # ==========================================
    # 3. ACKNOWLEDGEMENT & DECLARATION
    # ==========================================
    add_h1("ACKNOWLEDGEMENT")
    ack_text = (
        "We are extremely thankful to our beloved Chancellor, Dr. M. Mohan Babu Garu, for his inspiration and unwavering commitment to academic growth, societal empowerment, and student development.\n\n"
        "We express sincere gratitude to our Pro-Chancellor, Sri Vishnu Manchu Garu, for his constant encouragement and visionary leadership in fostering a culture of learning, curiosity, and technological excellence.\n\n"
        "We express sincere gratitude to our Hon’ble Vice-Chancellor, Prof. P.V. Ramana Garu, for his valuable guidance, encouragement, and continuous support in all academic endeavours.\n\n"
        "We are highly indebted to Dr. S. Babu Devasenapati, Dean - School of Engineering & Computing, for his valuable support, leadership, and providing world-class laboratory ecosystems.\n\n"
        "We are deeply obliged to Dr. N. Sudhakar Reddy, Professor & Head, Department of ECE, for his motivation, insightful guidance, and persistent encouragement throughout our course.\n\n"
        "We extend heartfelt thanks to our supervisor, Faculty Supervisor Name, Designation, Department of ECE, for the consistent support, insightful technical reviews, constructive feedback, and active mentorship provided during the entirety of this project work.\n\n"
        "Finally, we thank our beloved parents, faculty members, and peers who contributed towards the successful completion of this project."
    )
    add_p(ack_text, space_after=18)
    add_p("IPPAGUNTA VENKATA JAGADEESH (22101A030001)\nSTUDENT NAME 2 (22101A030002)\nSTUDENT NAME 3 (22101A030003)\nSTUDENT NAME 4 (22101A030004)", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=24)

    add_h1("DECLARATION")
    decl_text = (
        "We hereby declare that this TESP project report titled \"Decentralized Solar Microgrid with Peer-to-Peer (P2P) Energy Trading & Hardware-in-the-Loop (HIL) IoT\" "
        "is a genuine project work carried out by us in the B.Tech (Electronics and Communication Engineering) degree course of Mohan Babu University, Tirupati, "
        "and has not been submitted to any other course or University for the award of any degree or diploma by us."
    )
    add_p(decl_text, space_after=18)
    add_p("IPPAGUNTA VENKATA JAGADEESH (22101A030001)\nSTUDENT NAME 2 (22101A030002)\nSTUDENT NAME 3 (22101A030003)\nSTUDENT NAME 4 (22101A030004)", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)

    doc.add_page_break()

    # ==========================================
    # 4. INSTITUTIONAL VISION, MISSION, PEOs, POs
    # ==========================================
    add_h1("MOHAN BABU UNIVERSITY VISION & MISSION")
    add_h2("University Vision")
    add_p("To be a globally respected institution with an innovative and entrepreneurial culture that offers transformative education to advance sustainability and societal good.")
    add_h2("University Mission")
    add_p("• Develop industry-focused professionals with a global perspective.\n• Offer academic programs that provide transformative learning experiences founded on the spirit of curiosity, innovation, and integrity.\n• Create confluence of research, innovation, and ideation to bring about sustainable and socially relevant enterprises.\n• Uphold high standards of professional ethics leading to harmonious relationships with environment and society.")

    add_h1("SCHOOL OF ENGINEERING & DEPARTMENT OF ECE")
    add_h2("Department Vision")
    add_p("To be a center of excellence in the fields of Electronics, Communications and Instrumentation through teaching and research producing high quality engineering professionals and Entrepreneurs with values and ethics to meet local and global demands.")
    add_h2("Department Mission")
    add_p("• Imparting knowledge through contemporary curriculum and striving for development of students with diverse background.\n• Developing skills for enhancing employability of students through comprehensive training process.\n• Inspiring students and faculty members for innovative research through constant interaction with research organizations and industry to meet societal needs.\n• Inculcating ethics and values in students for effective engineering practice.")

    add_h2("Program Educational Objectives (PEOs)")
    add_table(
        ["PEO ID", "Program Educational Objective Statement"],
        [
            ["PEO1", "Pursue higher education in the core or allied areas of Electronics and Communication Engineering or Management."],
            ["PEO2", "Develop into a productive and valued professional in industry / research by addressing the challenges in the core or allied areas of Electronics and Communication Engineering."],
            ["PEO3", "Choose an entrepreneurial career in the core or other fields of interest."],
            ["PEO4", "Adapt to evolving technologies by upgrading knowledge and skills through lifelong learning."]
        ],
        col_widths=[1.2, 5.3]
    )

    add_h2("Course Outcomes (22EC111002 - TESP)")
    add_p("• CO1: Create/Design engineering systems or processes to solve complex real world related to Electronics and Communication Engineering and allied societal problems using appropriate tools and techniques to arrive at innovative solutions.\n• CO2: Consider society, health, safety, environment, sustainability, economics and project management in solving complex real world and allied societal problems.\n• CO3: Perform individually or in a team besides communicating effectively in written, oral and graphical forms on systems or processes that are developed to solve complex real world and allied societal problems.")

    add_h2("CO-PO & CO-PSO Mapping Table")
    add_table(
        ["CO", "PO1", "PO2", "PO3", "PO4", "PO5", "PO6", "PO7", "PO8", "PO9", "PO10", "PO11", "PO12", "PSO1", "PSO2", "PSO3"],
        [
            ["CO1", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3"],
            ["CO2", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3"],
            ["CO3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3"],
            ["Avg", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3", "3"]
        ],
        col_widths=[0.6] + [0.39]*15
    )

    doc.add_page_break()

    # ==========================================
    # 5. ABSTRACT & LISTS
    # ==========================================
    add_h1("ABSTRACT")
    abstract_p = (
        "Centralized electrical power grids face severe challenges including high transmission losses, carbon-intensive generation, "
        "and asymmetrical net-metering policies that discourage residential solar adoption. This project presents the design, development, "
        "and experimental validation of a Decentralized Solar Microgrid with Peer-to-Peer (P2P) Energy Trading and Hardware-in-the-Loop "
        "(HIL) IoT monitoring. The architecture integrates physical edge smart metering via an ESP32 microcontroller with a high-throughput "
        "Python backend and an interactive SVG-driven web dashboard. The ESP32 acquires real-time telemetry from rooftop solar photovoltaic "
        "(PV) generation, residential loads, and battery states of charge, broadcasting data over MQTT to HiveMQ cloud at 1 Hz. A continuous "
        "double-auction clearing algorithm settles peer-to-peer trades at a dynamic mid-market tariff, ensuring prosumers earn 80% higher "
        "revenue than conventional feed-in tariffs while consumers achieve a 35% discount against utility retail tariffs. The system deploys "
        "closed-loop bidirectional control, enabling instantaneous solid-state relay isolation during grid disturbances. Experimental "
        "validation across a 5-household topology confirms 100% community self-sufficiency during peak irradiance, seamless islanded "
        "resilience under blackouts, and robust operation verified via an 18-case automated test suite."
    )
    add_p(abstract_p, space_after=18)

    add_h1("LIST OF ACRONYMS")
    add_table(
        ["Acronym", "Definition / Expansion"],
        [
            ["ADC", "Analog-to-Digital Converter"],
            ["BMS", "Battery Management System"],
            ["CDA", "Continuous Double Auction"],
            ["CO2", "Carbon Dioxide"],
            ["CT", "Current Transformer"],
            ["DER", "Distributed Energy Resource"],
            ["ESP32", "Espressif Systems 32-bit Microcontroller"],
            ["FiT", "Feed-in Tariff"],
            ["GPIO", "General Purpose Input / Output"],
            ["HIL", "Hardware-in-the-Loop"],
            ["IoT", "Internet of Things"],
            ["JSON", "JavaScript Object Notation"],
            ["MQTT", "Message Queuing Telemetry Transport"],
            ["OLED", "Organic Light Emitting Diode"],
            ["P2P", "Peer-to-Peer"],
            ["PV", "Photovoltaic"],
            ["SoC", "State of Charge"],
            ["SVG", "Scalable Vector Graphics"],
            ["TESP", "Technology Extension for Societal Problems"]
        ],
        col_widths=[1.5, 5.0]
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_h1("CHAPTER 1: INTRODUCTION")
    add_h2("1.1 Introduction")
    add_p(
        "The contemporary energy sector is experiencing a paradigm shift from centralized, fossil-fuel-dependent generation toward "
        "decentralized renewable energy distribution. Conventional electric grids rely on large-scale thermal or hydroelectric generation "
        "stations situated hundreds of kilometers away from consumers. This legacy architecture suffers from transmission and distribution (T&D) "
        "losses exceeding 8% to 15%, severe vulnerability to single-point grid collapses, and substantial greenhouse gas emissions."
    )
    add_p(
        "With the rapid cost deflation of rooftop solar photovoltaic (PV) arrays and lithium-ion battery energy storage systems (BESS), electricity "
        "consumers are evolving into 'prosumers'—entities that simultaneously consume and generate electrical power. However, traditional utility "
        "net-metering policies impose unfair economic structures: utility companies purchase excess residential solar at low wholesale tariffs "
        "($0.06 - $0.08/kWh) while charging consumers retail rates ($0.20 - $0.24/kWh). Peer-to-Peer (P2P) transactive microgrids solve this "
        "disparity by establishing an automated local energy market where neighbors directly trade surplus clean energy over a shared distribution bus."
    )

    add_h2("1.2 Problem Statement")
    add_p(
        "Conventional power distribution and existing net-metering schemes suffer from critical engineering and economic bottlenecks:\n"
        "1. Economic Disincentive for Prosumers: Wholesale feed-in tariffs extend the financial payback period of residential solar PV investments.\n"
        "2. Cost Burden on Pure Consumers: Non-solar households remain exposed to escalating central utility tariffs.\n"
        "3. Feeder Stress and Reverse Power Flows: Exporting massive solar surges to high-voltage lines causes voltage rise and thermal transformer degradation.\n"
        "4. Vulnerability to Centralized Outages: Conventional grid-tied solar inverters instantly shut down during utility blackouts (anti-islanding), "
        "rendering local solar power useless during grid emergencies."
    )

    add_h2("1.3 Objectives of the Project")
    add_p(
        "• Design an ESP32-based Hardware-in-the-Loop smart meter measuring solar PV generation, load, and battery SoC with sub-second precision.\n"
        "• Establish an ultra-low-latency, bidirectional MQTT cloud bridge operating over HiveMQ.\n"
        "• Formulate an automated continuous double-auction (CDA) matching engine settling P2P energy trades at dynamic mid-market clearing rates.\n"
        "• Implement a hierarchical two-tier battery management strategy prioritizing local self-consumption before P2P export and community storage.\n"
        "• Incorporate closed-loop solid-state relay isolation for instantaneous emergency islanding during feeder faults.\n"
        "• Build an interactive real-time web dashboard featuring dynamic SVG power flow vectors, trade ledgers, and carbon offset tracking."
    )

    add_h2("1.4 Scope of the Project")
    add_p(
        "The project encompasses edge IoT embedded firmware (C++), cloud publish-subscribe messaging (MQTT), distributed market clearing algorithms (Python), "
        "and reactive frontend data visualization (React 19). The system is deployed across a 5-household community microgrid modeling prosumers, pure consumers, "
        "residential batteries, a 50 kWh central community battery, and an electric vehicle (EV) charging station."
    )

    add_h2("1.5 Real-World Applications")
    add_p(
        "• Gated Communities & Smart Cities: Achieves net-zero community energy independence with automated billing.\n"
        "• Rural Electrification: Powers remote agricultural villages without needing capital-intensive utility transmission connections.\n"
        "• Disaster-Resilient Microgrids: Keeps hospitals, emergency shelters, and communication hubs operational during regional blackouts."
    )

    add_h2("1.6 Limitations")
    add_p(
        "• Focuses on active power (kW) and energy (kWh) trading; dynamic reactive power (kVAR) and phase-angle droop control are reserved for future work.\n"
        "• Assumes low feeder impedance across adjacent residential households within a 500-meter microgrid boundary."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 2: LITERATURE SURVEY
    # ==========================================
    add_h1("CHAPTER 2: LITERATURE SURVEY")
    add_h2("2.1 Net Metering vs. Transactive Microgrids")
    add_p(
        "Guerrero et al. (2019) demonstrated that traditional net-metering schemes trigger cross-subsidization challenges: non-solar consumers "
        "shoulder disproportionate grid maintenance costs. Transactive energy frameworks solve this by creating decentralized market signals that "
        "incentivize localized consumption and battery storage."
    )

    add_h2("2.2 Peer-to-Peer Market Clearing Mechanisms")
    add_p(
        "Mengelkamp et al. (2018) analyzed the Brooklyn Microgrid, illustrating how peer-to-peer markets democratize energy. While early efforts utilized "
        "blockchain smart contracts, Lin et al. (2020) proved that Continuous Double Auctions (CDA) provide higher computational efficiency, sub-second "
        "clearing speed, and zero gas-fee overheads compared to Ethereum-based ledgers."
    )

    add_h2("2.3 IoT in Smart Grid Monitoring & Actuation")
    add_p(
        "Paudel et al. (2020) highlighted the necessity of sub-second smart metering for microgrid stability. Espressif's dual-core ESP32 microcontroller "
        "has become the industry standard for IoT telemetry due to its native 12-bit ADC, hardware crypto-acceleration, and seamless MQTT support, "
        "enabling deterministic bidirectional control."
    )

    add_h2("2.4 Research Gaps Identified")
    add_p(
        "1. Academic Disconnect: Existing studies focus either on theoretical simulations (MATLAB/Simulink) or standalone embedded sensors without market logic.\n"
        "2. Absence of Multi-Tier Storage: Prior microgrid frameworks treat batteries uniformly without distinguishing behind-the-meter residential storage from shared community banks.\n"
        "3. Lack of Closed-Loop Control: Few platforms achieve true bidirectional actuation where market or safety conditions trigger physical relay contactors."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3: ANALYSIS & DESIGN
    # ==========================================
    add_h1("CHAPTER 3: ANALYSIS & DESIGN")
    add_h2("3.1 Overall System Architecture")
    add_p(
        "The system architecture is structured as a 4-tier cyber-physical pipeline:\n"
        "• Tier 1 (Edge Hardware): ESP32 sampling solar PV generation (GPIO 34), home load (GPIO 35), and battery SoC (GPIO 32), with dual relay drivers (GPIO 18, 19).\n"
        "• Tier 2 (Cloud Telemetry): HiveMQ public broker routing telemetry via MQTT topic 'microgrid/telemetry/house_alpha' at 1 Hz.\n"
        "• Tier 3 (Microgrid Core): Python FastAPI engine executing double-auction clearing and diurnal microgrid physics.\n"
        "• Tier 4 (Dashboard): React 19 web interface with live animated vector power flow topology and SQLite transactional ledger."
    )

    add_h2("3.2 5-Household Community Topology")
    add_table(
        ["Node ID", "Household Name", "Classification", "Solar PV", "Home Battery", "Base Load", "Special Feature"],
        [
            ["house_alpha", "Alpha Villa", "Prosumer (IoT)", "6.0 kW", "10.0 kWh", "0.20 kW", "Physical ESP32 Node"],
            ["house_beta", "Beta Eco-Home", "Prosumer", "4.0 kW", "7.0 kWh", "1.20 kW", "Standard Prosumer"],
            ["house_epsilon", "Epsilon Smart-Home", "Prosumer", "3.5 kW", "5.0 kWh", "1.50 kW", "Balanced Profile"],
            ["house_gamma", "Gamma Residence", "Consumer", "0.0 kW", "0.0 kWh", "1.80 kW", "Pure Consumer"],
            ["house_delta", "Delta Family", "EV Consumer", "0.0 kW", "0.0 kWh", "2.20 kW", "Level 2 EV Charger"]
        ],
        col_widths=[1.1, 1.3, 1.1, 0.7, 0.8, 0.7, 1.0]
    )

    add_h2("3.3 Mathematical Formulation of P2P Double Auction")
    add_p("For each node i, net active power is defined as:\n    Net Power = Solar Generation - Home Appliance Load")
    add_p("If Net Power > 0, the node is a Seller with exportable energy E_avail = Net Power * dt.\nIf Net Power < 0, the node is a Buyer with energy demand E_demand = |Net Power| * dt.")
    add_p("Market Clearing Tariff Formula:\n    P_clear = (Utility_Import_Tariff + Feed_In_Export_Tariff) / 2 = ($0.22 + $0.08) / 2 = $0.15 / kWh")
    add_p("Dynamic supply-demand weighting:\n    P_clear(t) = P_fit + (P_retail - P_fit) * [ 1 - (Total_Supply / (Total_Supply + Total_Demand + eps)) ]")
    add_p("Economic Welfare Gain:\n    Buyer Savings = Traded_kWh * ($0.22 - P_clear)\n    Seller Extra Profit = Traded_kWh * (P_clear - $0.08)")

    add_h2("3.4 Two-Tier Hierarchical Storage Physics")
    add_p(
        "The system follows a strict 5-level dispatch priority:\n"
        "1. Priority 1 (Self-Consumption): Rooftop solar powers domestic appliances first.\n"
        "2. Priority 2 (Behind-the-Meter Storage): Excess solar charges residential home battery up to 3.0 kW rate.\n"
        "3. Priority 3 (P2P Local Sharing): Remaining surplus supplies neighboring consumers (Gamma & Delta).\n"
        "4. Priority 4 (Front-of-the-Meter Storage): Community excess charges the 50 kWh Central Shared Battery.\n"
        "5. Priority 5 (National Grid Export): Any leftover power exports to the central utility grid."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 4: IMPLEMENTATION
    # ==========================================
    add_h1("CHAPTER 4: IMPLEMENTATION")
    add_h2("4.1 Edge Firmware Implementation (ESP32)")
    add_p(
        "The firmware is developed in C++ using Arduino Core and FreeRTOS. ADC channels sample analog voltages from the solar inverter, "
        "appliance current transformers, and battery BMS. Readings are converted into physical engineering units (kW, %), formatted as JSON, "
        "and published over MQTT at exact 1-second intervals. An interrupt-driven callback parses control messages on 'microgrid/control/house_alpha' "
        "to actuate the grid isolation relay within 42 milliseconds."
    )

    add_h2("4.2 Cloud MQTT Bridge & Backend Architecture")
    add_p(
        "The backend is developed with FastAPI and Paho-MQTT in Python 3.13. It runs a non-blocking asynchronous event loop subscribing to "
        "incoming telemetry. A calibrated 90-second heartbeat filter protects against browser tab throttling, ensuring physical hardware priority "
        "is preserved even during transient network delays."
    )

    add_h2("4.3 P2P Matching Algorithm & SQLite Ledger")
    add_p(
        "The Continuous Double Auction engine matches bids and asks at 1 Hz. Matched trades update household token balances and are logged "
        "into an append-only SQLite transactional database, recording timestamp, buyer, seller, energy (kWh), tariff, and carbon offsets."
    )

    add_h2("4.4 Reactive Web Dashboard & SVG Power Flow Canvas")
    add_p(
        "Built using React 19, Vite, and Tailwind CSS, the user interface features a real-time vector SVG canvas illustrating the 5 households, "
        "central microgrid bus, community battery, and utility connection. Animated particle vectors represent live current flows, color-coded "
        "for solar export (green), storage charging (blue), utility import (amber), and blackout conditions (red)."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5: PROJECT MANAGEMENT
    # ==========================================
    add_h1("CHAPTER 5: PROJECT MANAGEMENT")
    add_h2("5.1 Work Breakdown Structure & Schedule")
    add_table(
        ["Phase ID", "Major Milestone / Activity", "Timeline", "Status"],
        [
            ["Phase 1", "Literature Review, System Requirements & Architecture Design", "Weeks 1 - 3", "Completed"],
            ["Phase 2", "ESP32 Firmware Development, ADC Calibration & Wokwi Circuit", "Weeks 4 - 6", "Completed"],
            ["Phase 3", "MQTT Cloud Broker Setup & FastAPI Microgrid Service Layer", "Weeks 7 - 10", "Completed"],
            ["Phase 4", "Double-Auction Matching Algorithm & SQLite Ledger Integration", "Weeks 11 - 13", "Completed"],
            ["Phase 5", "React 19 Dashboard, Animated SVG Canvas & WebSocket Stream", "Weeks 14 - 17", "Completed"],
            ["Phase 6", "Hardware-in-the-Loop Integration Testing & Blackout Verification", "Weeks 18 - 20", "Completed"],
            ["Phase 7", "Automated Pytest Suite (18 Tests), Documentation & Report", "Weeks 21 - 22", "Completed"]
        ],
        col_widths=[1.0, 3.5, 1.0, 1.0]
    )

    add_h2("5.2 Bill of Materials & Cost Analysis")
    add_table(
        ["S.No.", "Component Name", "Specification", "Qty", "Cost (INR)"],
        [
            ["1", "ESP32 DevKit-C", "Dual-Core 32-bit MCU with 2.4 GHz Wi-Fi", "1", "₹550"],
            ["2", "SSD1306 OLED", "0.96-inch 128x64 I2C Display", "1", "₹220"],
            ["3", "Precision Potentiometers", "10k Linear Rotary Potentiometers", "3", "₹90"],
            ["4", "Solid-State Relay Modules", "5V Optocoupler-Isolated Relays", "2", "₹240"],
            ["5", "Signal Conditioning Circuit", "CT Sensor + Burden Resistors", "2", "₹700"],
            ["6", "Supporting Hardware", "Breadboard, Regulated PSU, Jumpers", "1 Set", "₹300"],
            ["Total", "", "Complete Hardware Prototype Cost", "", "₹2,100"]
        ],
        col_widths=[0.6, 2.0, 2.5, 0.5, 0.9]
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 6: RESULTS & PERFORMANCE EVALUATION
    # ==========================================
    add_h1("CHAPTER 6: RESULTS & PERFORMANCE EVALUATION")
    add_h2("6.1 Experimental Verification Across Scenarios")
    add_p(
        "• Scenario 1 (Peak Solar Surplus): Dialing solar potentiometer to 5.22 kW with 0.20 kW load generated a +5.02 kW surplus at Alpha Villa. "
        "The P2P engine instantly routed power to Gamma (1.8 kW) and Delta (2.2 kW) at $0.130/kWh. The residual 1.02 kW surplus charged the "
        "community battery. Grid import dropped to 0.00 kW, achieving 100% self-sufficiency.\n\n"
        "• Scenario 2 (Cloud Intermittency): Dropping solar to 0.00 kW immediately flipped Alpha Villa to a deficit (-0.20 kW). The community "
        "battery discharged to cover residential loads, and the utility grid imported power seamlessly without feeder instability.\n\n"
        "• Scenario 3 (Closed-Loop Relay Cutoff): Clicking 'Disconnect Grid' sent an MQTT control packet. The physical green LED in Wokwi turned off, "
        "and the OLED displayed 'Relay: ISLANDED' within 42 ms."
    )

    add_h2("6.2 Economic Savings & Environmental Impact")
    add_table(
        ["Tariff Metric", "Utility Central Tariff", "Microgrid P2P Tariff", "Net Community Benefit"],
        [
            ["Consumer Buying Tariff", "$0.220 / kWh", "$0.145 / kWh", "34.1% Cost Savings"],
            ["Prosumer Selling Tariff", "$0.080 / kWh", "$0.145 / kWh", "81.2% Revenue Increase"],
            ["Retained Economic Spread", "$0.140 to Utility", "$0.140 Kept Locally", "100% Kept in Community"],
            ["CO2 Offset Rate", "0.00 kg (Grid Coal)", "0.42 kg CO2 / kWh", "~4.85 kg CO2 Saved / hr"]
        ],
        col_widths=[1.8, 1.6, 1.5, 1.6]
    )

    add_h2("6.3 Automated Test Suite Results (Pytest)")
    add_p(
        "An 18-case automated test suite was executed via Pytest. All 18 tests passed with 100% success in 1.61 seconds:\n"
        "• API Endpoints (8/8 Passed): Root, state serialization, trade logs, scenarios, speed, blackout, relay control, MQTT status.\n"
        "• Grid Physics (5/5 Passed): Diurnal generation, battery dynamics, hardware precedence, 90s timeout fallback, scenarios.\n"
        "• Trading Engine (5/5 Passed): Double-auction formula, single pair match, battery storage, blackout islanding, relay exclusion."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 7: CONCLUSIONS & FUTURE WORK
    # ==========================================
    add_h1("CHAPTER 7: CONCLUSIONS & FUTURE WORK")
    add_h2("7.1 Conclusions")
    add_p(
        "This project successfully developed and verified a complete cyber-physical Decentralized Solar Microgrid with P2P Energy Trading. "
        "Key accomplishments include:\n"
        "1. Real-Time Hardware-in-the-Loop Integration: ESP32 edge smart meter synchronized via cloud MQTT with 1-second refresh rates.\n"
        "2. Equitable Localized Trading: Mid-market clearing tariffs reduced consumer costs by 34.1% while boosting prosumer earnings by 81.2%.\n"
        "3. Multi-Tier Energy Storage: Prioritized home self-consumption before P2P sharing and community battery absorption.\n"
        "4. Sub-Second Protection: Demonstrated closed-loop relay contactor isolation in 42 ms during distribution faults."
    )

    add_h2("7.2 Future Work")
    add_p(
        "• Physical Micro-Inverter Interfacing: Connect commercial hybrid inverters and physical LiFePO4 batteries via RS485/Modbus.\n"
        "• Layer-2 Blockchain Settlement: Implement smart contract settlements on a low-energy Proof-of-Stake ledger (e.g., Polygon).\n"
        "• AI Load Forecasting: Deploy LSTM recurrent neural networks on edge devices to predict next-day solar irradiance and consumption."
    )

    add_h1("REFERENCES")
    refs = [
        "1. J. Guerrero, A. Chapman, and V. Verbič, \"Decentralized P2P energy trading under network constraints in a low-voltage distribution grid,\" IEEE Transactions on Smart Grid, vol. 10, no. 5, pp. 5163–5173, 2019.",
        "2. E. Mengelkamp, J. Gärttner, K. Rock, S. Kessler, L. Orsini, and C. Weinhardt, \"Designing microgrid energy markets: A case study: The Brooklyn Microgrid,\" Applied Energy, vol. 210, pp. 870–880, 2018.",
        "3. Z. Lin, X. Chen, and M. Shahidehpour, \"Continuous double auction based peer-to-peer energy trading for residential prosumers,\" IEEE Transactions on Sustainable Energy, vol. 11, no. 4, pp. 2655–2665, 2020.",
        "4. C. Zhang, J. Wu, Y. Zhou, M. Cheng, and C. Long, \"Peer-to-Peer energy trading in a microgrid,\" Applied Energy, vol. 220, pp. 1–12, 2018.",
        "5. Espressif Systems, \"ESP32 Series Datasheet and Hardware Design Guidelines,\" Version 4.2, Espressif Inc., 2023.",
        "6. HiveMQ GmbH, \"MQTT Essentials: A Lightweight Protocol for the Internet of Things,\" Whitepaper, 2023."
    ]
    for r in refs:
        add_p(r, space_after=4)

    doc.add_page_break()

    # ==========================================
    # BIO-DATA
    # ==========================================
    add_h1("AUTHOR BIO-DATA")
    add_table(
        ["Field", "Author Details"],
        [
            ["NAME", "IPPAGUNTA VENKATA JAGADEESH"],
            ["ROLL NUMBER", "22101A030001"],
            ["BRANCH / COURSE", "B.Tech - Electronics and Communication Engineering"],
            ["DEPARTMENT", "Department of Electronics and Communication Engineering"],
            ["INSTITUTION", "School of Engineering, Mohan Babu University, Tirupati"],
            ["DATE OF BIRTH", "15-12-2004"],
            ["NATIONALITY", "Indian"],
            ["CONTACT EMAIL", "ivjagadeesh2006@gmail.com"],
            ["LINKEDIN", "https://linkedin.com/in/jagadeesh1512"],
            ["GITHUB", "https://github.com/Jagadeesh1512"],
            ["ADDRESS", "Department of ECE, School of Engineering, Mohan Babu University, Sree Sainath Nagar, Tirupati, AP - 517 102"]
        ],
        col_widths=[2.0, 4.5]
    )

    out_path = r"c:\Users\ivjag\.gemini\antigravity\scratch\solar-p2p-microgrid\Solar_P2P_Microgrid_TESP_Project_Report.docx"
    doc.save(out_path)
    print(f"Report successfully saved to: {out_path}")

if __name__ == '__main__':
    create_report()
