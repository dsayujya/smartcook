import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

output_dir = r"d:/smartcook/report_assets"
os.makedirs(output_dir, exist_ok=True)

# Common styling configuration
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# ==============================================================================
# 1. Figure 4.1: High-Level System Architecture Diagram
# ==============================================================================
def draw_system_architecture():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    # Background canvas
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    # Title
    ax.text(5.5, 7.1, "Figure 4.1: Three-Tier Distributed System Architecture of SmartCook", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1A202C')

    # Tiers Boxes
    # Tier 1: Presentation Tier
    tier1 = patches.FancyBboxPatch((0.5, 4.4), 3.0, 2.3, boxstyle="round,pad=0.15", ec="#2B6CB0", fc="#EBF8FF", lw=2)
    ax.add_patch(tier1)
    ax.text(2.0, 6.4, "PRESENTATION TIER\n(Flutter Cross-Platform Mobile)", ha='center', va='center', fontsize=10, fontweight='bold', color='#2B6CB0')
    
    comp1 = ["• Camera & Gallery Scanner", "• Provider Reactive State", "• Bounded Filter Drawer UI", "• SharedPreferences Cache", "• Responsive Material 3"]
    for i, c in enumerate(comp1):
        ax.text(0.7, 5.9 - (i * 0.32), c, fontsize=8.5, color='#2D3748')

    # Tier 2: Application Tier
    tier2 = patches.FancyBboxPatch((4.0, 3.4), 3.3, 3.3, boxstyle="round,pad=0.15", ec="#2F855A", fc="#F0FFF4", lw=2)
    ax.add_patch(tier2)
    ax.text(5.65, 6.4, "APPLICATION TIER\n(FastAPI ASGI Microservices)", ha='center', va='center', fontsize=10, fontweight='bold', color='#2F855A')

    comp2 = [
        "• REST API Gateway (Uvicorn)",
        "• Gemini Multimodal Vision Pipeline\n  (Cascading 10s Failover)",
        "• Synonym & Pantry Classifier\n  (70+ Kitchen Staples)",
        "• Dual-Mode Heuristic Scorer\n  (Basket Use vs Ready to Cook)",
        "• YouTube Media Sanitizer\n  (Excludes Medical Clickbait)",
        "• JWT Security & Token Guard"
    ]
    for i, c in enumerate(comp2):
        ax.text(4.2, 5.9 - (i * 0.44), c, fontsize=8.5, color='#2D3748')

    # Tier 3: Data Tier
    tier3 = patches.FancyBboxPatch((7.8, 4.4), 2.7, 2.3, boxstyle="round,pad=0.15", ec="#744210", fc="#FFFAF0", lw=2)
    ax.add_patch(tier3)
    ax.text(9.15, 6.4, "DATABASE TIER\n(PostgreSQL Relational Storage)", ha='center', va='center', fontsize=10, fontweight='bold', color='#744210')

    comp3 = ["• 5,900+ Culinary Recipes", "• Thousands of Ingredients", "• 3NF Associative Schemas", "• Case-Insensitive ILIKE Indexes", "• SQL Match Pre-Filter Engine"]
    for i, c in enumerate(comp3):
        ax.text(8.0, 5.9 - (i * 0.32), c, fontsize=8.5, color='#2D3748')

    # External AI Cloud Services
    ext_ai = patches.FancyBboxPatch((1.5, 0.8), 3.5, 1.8, boxstyle="round,pad=0.15", ec="#805AD5", fc="#FAF5FF", lw=2)
    ax.add_patch(ext_ai)
    ax.text(3.25, 2.2, "EXTERNAL AI VISION SERVICE", ha='center', va='center', fontsize=10, fontweight='bold', color='#805AD5')
    ax.text(3.25, 1.6, "Google Gemini Vision API\n(gemini-3.1-flash-lite, 3.6-flash)\nMultimodal zero-shot image parser", ha='center', va='center', fontsize=8.5, color='#4A5568')

    # External Media Cloud Services
    ext_yt = patches.FancyBboxPatch((6.0, 0.8), 3.5, 1.8, boxstyle="round,pad=0.15", ec="#C53030", fc="#FFF5F5", lw=2)
    ax.add_patch(ext_yt)
    ax.text(7.75, 2.2, "EXTERNAL MEDIA SERVICE", ha='center', va='center', fontsize=10, fontweight='bold', color='#C53030')
    ax.text(7.75, 1.6, "Google YouTube Data API v3\nTargeted cooking tutorial search\nFiltered category index", ha='center', va='center', fontsize=8.5, color='#4A5568')

    # Connectors
    # Flutter <-> FastAPI
    ax.annotate("", xy=(4.0, 5.3), xytext=(3.5, 5.3),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#4A5568"))
    ax.text(3.75, 5.5, "HTTPS / JSON\nREST API", ha='center', va='bottom', fontsize=7.5, color='#4A5568', fontweight='bold')

    # FastAPI <-> PostgreSQL
    ax.annotate("", xy=(7.8, 5.3), xytext=(7.3, 5.3),
                arrowprops=dict(arrowstyle="<->", lw=2, color="#4A5568"))
    ax.text(7.55, 5.5, "SQLAlchemy\nTCP Pool", ha='center', va='bottom', fontsize=7.5, color='#4A5568', fontweight='bold')

    # FastAPI <-> Gemini
    ax.annotate("", xy=(3.5, 2.6), xytext=(5.0, 3.4),
                arrowprops=dict(arrowstyle="<->", lw=1.8, color="#805AD5", ls="--"))
    ax.text(4.0, 2.9, "gRPC / REST", fontsize=7.5, color='#805AD5', fontweight='bold')

    # FastAPI <-> YouTube API
    ax.annotate("", xy=(7.5, 2.6), xytext=(6.2, 3.4),
                arrowprops=dict(arrowstyle="<->", lw=1.8, color="#C53030", ls="--"))
    ax.text(7.0, 2.9, "HTTPS REST", fontsize=7.5, color='#C53030', fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_1_system_architecture.png")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print("Saved:", path)

# ==============================================================================
# 2. Figure 4.2: Data Flow Diagram Level 0 (Context Diagram)
# ==============================================================================
def draw_dfd_level_0():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    ax.text(5.0, 5.6, "Figure 4.2: Data Flow Diagram (DFD Level 0 - Context Level)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1A202C')

    # Central System Process (Circle)
    circ = patches.Circle((5.0, 2.8), radius=1.3, fc='#EBF8FF', ec='#2B6CB0', lw=2.5)
    ax.add_patch(circ)
    ax.text(5.0, 3.1, "Process 0.0", ha='center', va='center', fontsize=10, fontweight='bold', color='#2B6CB0')
    ax.text(5.0, 2.6, "SMARTCOOK\nCORE SYSTEM", ha='center', va='center', fontsize=11, fontweight='bold', color='#1A365D')

    # External Entity: User / Home Cook
    user_box = patches.Rectangle((0.5, 1.8), 2.0, 2.0, fc='#EDF2F7', ec='#4A5568', lw=2)
    ax.add_patch(user_box)
    ax.text(1.5, 2.8, "USER /\nHOME COOK", ha='center', va='center', fontsize=10, fontweight='bold', color='#2D3748')

    # External Entity: Google Gemini Vision
    gemini_box = patches.Rectangle((7.5, 3.6), 2.0, 1.5, fc='#FAF5FF', ec='#805AD5', lw=2)
    ax.add_patch(gemini_box)
    ax.text(8.5, 4.35, "GOOGLE GEMINI\nVISION API", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#6B46C1')

    # External Entity: YouTube Data API
    yt_box = patches.Rectangle((7.5, 1.0), 2.0, 1.5, fc='#FFF5F5', ec='#C53030', lw=2)
    ax.add_patch(yt_box)
    ax.text(8.5, 1.75, "YOUTUBE DATA\nAPI v3", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#9B2C2C')

    # Flows between User and System
    ax.annotate("", xy=(3.7, 3.3), xytext=(2.5, 3.3), arrowprops=dict(arrowstyle="->", lw=1.8, color="#2B6CB0"))
    ax.text(3.1, 3.5, "Raw Photo / Groceries", ha='center', va='bottom', fontsize=8, color='#2B6CB0', fontweight='bold')

    ax.annotate("", xy=(3.7, 2.8), xytext=(2.5, 2.8), arrowprops=dict(arrowstyle="->", lw=1.8, color="#2B6CB0"))
    ax.text(3.1, 2.5, "Culinary Filters & Mode", ha='center', va='top', fontsize=8, color='#2B6CB0', fontweight='bold')

    ax.annotate("", xy=(2.5, 2.1), xytext=(3.7, 2.1), arrowprops=dict(arrowstyle="->", lw=1.8, color="#2F855A"))
    ax.text(3.1, 1.8, "Ranked Recipes & Steps", ha='center', va='top', fontsize=8, color='#2F855A', fontweight='bold')

    # Flows between System and Gemini
    ax.annotate("", xy=(7.5, 4.4), xytext=(6.3, 3.6), arrowprops=dict(arrowstyle="->", lw=1.8, color="#805AD5"))
    ax.text(6.8, 4.2, "Image Bytes", fontsize=8, color='#805AD5', fontweight='bold')

    ax.annotate("", xy=(6.2, 3.2), xytext=(7.5, 3.8), arrowprops=dict(arrowstyle="->", lw=1.8, color="#805AD5"))
    ax.text(7.2, 3.2, "Detected JSON", fontsize=8, color='#805AD5', fontweight='bold')

    # Flows between System and YouTube
    ax.annotate("", xy=(7.5, 2.1), xytext=(6.2, 2.4), arrowprops=dict(arrowstyle="->", lw=1.8, color="#C53030"))
    ax.text(6.7, 2.4, "Sanitized Query", fontsize=8, color='#C53030', fontweight='bold')

    ax.annotate("", xy=(6.0, 1.8), xytext=(7.5, 1.4), arrowprops=dict(arrowstyle="->", lw=1.8, color="#C53030"))
    ax.text(6.8, 1.3, "Video Metadata", fontsize=8, color='#C53030', fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_2_dfd_level_0.png")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print("Saved:", path)

# ==============================================================================
# 3. Figure 4.3: Data Flow Diagram Level 1
# ==============================================================================
def draw_dfd_level_1():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    ax.text(5.5, 6.7, "Figure 4.3: Data Flow Diagram (DFD Level 1 - Detailed Functional Pipeline)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1A202C')

    # Process 1.0: Vision Parsing
    p1 = patches.Circle((2.0, 5.0), radius=0.9, fc='#EBF8FF', ec='#2B6CB0', lw=2)
    ax.add_patch(p1)
    ax.text(2.0, 5.2, "1.0", ha='center', va='center', fontsize=9, fontweight='bold', color='#2B6CB0')
    ax.text(2.0, 4.8, "Vision Image\nParsing", ha='center', va='center', fontsize=9, fontweight='bold', color='#1A365D')

    # Process 2.0: Canonicalization & Synonym Mapping
    p2 = patches.Circle((5.5, 5.0), radius=0.9, fc='#F0FFF4', ec='#2F855A', lw=2)
    ax.add_patch(p2)
    ax.text(5.5, 5.2, "2.0", ha='center', va='center', fontsize=9, fontweight='bold', color='#2F855A')
    ax.text(5.5, 4.8, "Synonym &\nPantry Mapping", ha='center', va='center', fontsize=9, fontweight='bold', color='#1C4532')

    # Process 3.0: Candidate SQL Pre-Filter
    p3 = patches.Circle((9.0, 5.0), radius=0.9, fc='#FFFAF0', ec='#D69E2E', lw=2)
    ax.add_patch(p3)
    ax.text(9.0, 5.2, "3.0", ha='center', va='center', fontsize=9, fontweight='bold', color='#D69E2E')
    ax.text(9.0, 4.8, "Candidate SQL\nPre-Filter", ha='center', va='center', fontsize=9, fontweight='bold', color='#744210')

    # Process 4.0: Dual-Mode Heuristic Scorer
    p4 = patches.Circle((9.0, 2.0), radius=0.9, fc='#FAF5FF', ec='#805AD5', lw=2)
    ax.add_patch(p4)
    ax.text(9.0, 2.2, "4.0", ha='center', va='center', fontsize=9, fontweight='bold', color='#805AD5')
    ax.text(9.0, 1.8, "Dual-Mode\nScorer", ha='center', va='center', fontsize=9, fontweight='bold', color='#44337A')

    # Process 5.0: Video Tutorial Dispatcher
    p5 = patches.Circle((4.0, 2.0), radius=0.9, fc='#FFF5F5', ec='#E53E3E', lw=2)
    ax.add_patch(p5)
    ax.text(4.0, 2.2, "5.0", ha='center', va='center', fontsize=9, fontweight='bold', color='#E53E3E')
    ax.text(4.0, 1.8, "YouTube\nDispatcher", ha='center', va='center', fontsize=9, fontweight='bold', color='#742A2A')

    # Data Store: Database (open ended rectangle)
    db_store = patches.Rectangle((6.2, 3.2), 2.2, 0.9, fc='#EDF2F7', ec='#4A5568', lw=2)
    ax.add_patch(db_store)
    ax.text(7.3, 3.65, "D1: Recipes & Ingredients\n(5,900+ Records)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2D3748')

    # Arrows between processes
    # P1 -> P2
    ax.annotate("", xy=(4.6, 5.0), xytext=(2.9, 5.0), arrowprops=dict(arrowstyle="->", lw=1.8, color="#2B6CB0"))
    ax.text(3.75, 5.25, "Raw Tokens", ha='center', va='bottom', fontsize=8, color='#2B6CB0', fontweight='bold')

    # P2 -> P3
    ax.annotate("", xy=(8.1, 5.0), xytext=(6.4, 5.0), arrowprops=dict(arrowstyle="->", lw=1.8, color="#2F855A"))
    ax.text(7.25, 5.25, "Canonical Basket", ha='center', va='bottom', fontsize=8, color='#2F855A', fontweight='bold')

    # P3 <-> D1
    ax.annotate("", xy=(7.8, 4.1), xytext=(8.4, 4.5), arrowprops=dict(arrowstyle="<->", lw=1.8, color="#D69E2E"))

    # P3 -> P4
    ax.annotate("", xy=(9.0, 2.9), xytext=(9.0, 4.1), arrowprops=dict(arrowstyle="->", lw=1.8, color="#805AD5"))
    ax.text(9.1, 3.5, "Top 150 Candidates", ha='left', va='center', fontsize=8, color='#805AD5', fontweight='bold')

    # P4 -> P5
    ax.annotate("", xy=(4.9, 2.0), xytext=(8.1, 2.0), arrowprops=dict(arrowstyle="->", lw=1.8, color="#E53E3E"))
    ax.text(6.5, 2.25, "Selected Dish Title", ha='center', va='bottom', fontsize=8, color='#E53E3E', fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_3_dfd_level_1.png")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print("Saved:", path)

# ==============================================================================
# 4. Figure 4.4: UML Use Case Diagram
# ==============================================================================
def draw_uml_use_case():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    ax.text(5.0, 6.1, "Figure 4.4: UML Use Case Diagram for SmartCook", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1A202C')

    # System Boundary Box
    sys_box = patches.Rectangle((2.8, 0.5), 5.4, 5.2, fc='#FFFFFF', ec='#4A5568', lw=2, ls='--')
    ax.add_patch(sys_box)
    ax.text(5.5, 5.4, "SmartCook System Boundary", ha='center', va='center', fontsize=10, fontweight='bold', color='#4A5568')

    # Actor: Home Cook (Left)
    ax.plot([1.2, 1.2], [3.2, 3.8], lw=2.5, color='#2B6CB0') # body
    ax.plot([0.8, 1.6], [3.5, 3.5], lw=2.5, color='#2B6CB0') # arms
    ax.plot([1.2, 0.8], [3.2, 2.6], lw=2.5, color='#2B6CB0') # leg 1
    ax.plot([1.2, 1.6], [3.2, 2.6], lw=2.5, color='#2B6CB0') # leg 2
    head = patches.Circle((1.2, 4.1), radius=0.25, fc='#FFFFFF', ec='#2B6CB0', lw=2)
    ax.add_patch(head)
    ax.text(1.2, 2.3, "Home Cook\n(Mobile User)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1A365D')

    # Use Cases (Ellipses)
    use_cases = [
        ("Capture / Scan Ingredients", 4.7),
        ("Review & Edit Basket List", 4.0),
        ("Select Dietary & Time Filters", 3.3),
        ("Generate Ranked Recipes", 2.6),
        ("Follow Step-by-Step Guide", 1.9),
        ("Stream YouTube Video Tutorial", 1.2)
    ]

    for title, y in use_cases:
        el = patches.Ellipse((5.5, y), 3.8, 0.55, fc='#EBF8FF', ec='#2B6CB0', lw=1.5)
        ax.add_patch(el)
        ax.text(5.5, y, title, ha='center', va='center', fontsize=9, fontweight='bold', color='#1A365D')

        # Connect user to use case
        ax.plot([1.5, 3.6], [3.6, y], color='#4A5568', lw=1.2, alpha=0.7)

    # Secondary Actor: Gemini Vision API (Right Top)
    g_box = patches.Rectangle((8.6, 4.2), 1.2, 0.9, fc='#FAF5FF', ec='#805AD5', lw=1.8)
    ax.add_patch(g_box)
    ax.text(9.2, 4.65, "<<System>>\nGemini API", ha='center', va='center', fontsize=8, fontweight='bold', color='#6B46C1')
    ax.plot([7.4, 8.6], [4.7, 4.65], color='#805AD5', lw=1.5, ls=":")

    # Secondary Actor: YouTube Data API (Right Bottom)
    yt_box = patches.Rectangle((8.6, 0.9), 1.2, 0.9, fc='#FFF5F5', ec='#C53030', lw=1.8)
    ax.add_patch(yt_box)
    ax.text(9.2, 1.35, "<<System>>\nYouTube API", ha='center', va='center', fontsize=8, fontweight='bold', color='#9B2C2C')
    ax.plot([7.4, 8.6], [1.2, 1.35], color='#C53030', lw=1.5, ls=":")

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_4_uml_use_case.png")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print("Saved:", path)

# ==============================================================================
# 5. Figure 4.6: Entity Relationship (ER) Diagram
# ==============================================================================
def draw_er_diagram():
    fig, ax = plt.subplots(figsize=(15.5, 10.8), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 10.8)
    ax.axis('off')

    # Background canvas styling
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # Title & Subtitle
    ax.text(7.75, 10.35, "SmartCook Relational Database Entity-Relationship (ER) Diagram", 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#0F172A')
    ax.text(7.75, 10.02, "PostgreSQL 3NF Normalized Schema • Authentication, Multimodal Culinary Catalogue, and User Interaction Tiers", 
            ha='center', va='center', fontsize=9.5, color='#475569')

    # Helper function to draw entity tables
    def draw_entity(x, y, w, h, title, header_color, attrs):
        # Outer box with soft shadow border
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.14", 
                                     fc='#FFFFFF', ec=header_color, lw=2)
        ax.add_patch(box)
        
        # Header banner
        header_h = 0.52
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                        boxstyle="round,pad=0.06,rounding_size=0.12", 
                                        fc=header_color, ec=header_color, lw=1)
        ax.add_patch(header)
        ax.text(x + w / 2.0, y + h - header_h / 2.0, title, ha='center', va='center', 
                color='white', fontweight='bold', fontsize=10)

        # Attribute lines
        line_spacing = (h - header_h - 0.28) / max(len(attrs), 1)
        start_y = y + h - header_h - 0.22
        
        for i, (attr_name, attr_type, is_pk, is_fk) in enumerate(attrs):
            curr_y = start_y - (i * line_spacing)
            
            # Badge / Label
            prefix = ""
            tag_color = "#1E293B"
            if is_pk and is_fk:
                prefix = "PK, FK "
                tag_color = "#DC2626"
            elif is_pk:
                prefix = "PK "
                tag_color = "#D97706"
            elif is_fk:
                prefix = "FK "
                tag_color = "#2563EB"

            weight = 'bold' if (is_pk or is_fk) else 'normal'
            
            # Name
            ax.text(x + 0.16, curr_y, prefix + attr_name, fontsize=7.8, color=tag_color if prefix else '#334155', 
                    fontweight=weight, va='center')
            # Type
            ax.text(x + w - 0.16, curr_y, attr_type, fontsize=7.2, color='#64748B', 
                    ha='right', va='center', fontfamily='monospace')

    # 1. USERS Entity (Top Left)
    user_attrs = [
        ("id", "SERIAL", True, False),
        ("username", "VARCHAR(100) UQ", False, False),
        ("email", "VARCHAR(255) UQ", False, False),
        ("hashed_password", "VARCHAR(255)", False, False),
        ("full_name", "VARCHAR(100)", False, False),
        ("phone_number", "VARCHAR(20) UQ", False, False),
        ("is_email_verified", "BOOLEAN", False, False),
        ("is_phone_verified", "BOOLEAN", False, False),
        ("google_id", "VARCHAR(255) UQ", False, False),
        ("avatar_url", "VARCHAR(500)", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ]
    draw_entity(0.6, 4.6, 3.2, 4.9, "USERS", "#1D4ED8", user_attrs)

    # 2. USER_PREFERENCES Entity (Bottom Left)
    pref_attrs = [
        ("id", "SERIAL", True, False),
        ("user_id", "INT", False, True),
        ("diet_type", "VARCHAR(50)", False, False),
        ("cuisine_preference", "VARCHAR(100)", False, False),
        ("max_cooking_time", "INT", False, False),
        ("difficulty_preference", "VARCHAR(50)", False, False),
    ]
    draw_entity(0.6, 1.2, 3.2, 2.7, "USER_PREFERENCES", "#0D9488", pref_attrs)

    # 3. OTP_VERIFICATIONS Entity (Bottom Center-Left)
    otp_attrs = [
        ("id", "SERIAL", True, False),
        ("target", "VARCHAR(255)", False, False),
        ("otp_code", "VARCHAR(10)", False, False),
        ("otp_type", "VARCHAR(50)", False, False),
        ("expires_at", "TIMESTAMP", False, False),
        ("is_used", "BOOLEAN", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ]
    draw_entity(4.3, 0.9, 2.8, 3.0, "OTP_VERIFICATIONS", "#475569", otp_attrs)

    # 4. FAVORITES Entity (Top Center)
    fav_attrs = [
        ("id", "SERIAL", True, False),
        ("user_id", "INT", False, True),
        ("recipe_id", "INT", False, True),
    ]
    draw_entity(4.3, 7.6, 2.8, 1.9, "FAVORITES", "#7C3AED", fav_attrs)

    # 5. HISTORY Entity (Middle Center)
    hist_attrs = [
        ("id", "SERIAL", True, False),
        ("user_id", "INT", False, True),
        ("recipe_id", "INT", False, True),
        ("viewed_at", "VARCHAR(50)", False, False),
    ]
    draw_entity(4.3, 4.8, 2.8, 2.2, "HISTORY", "#8B5CF6", hist_attrs)

    # 6. RECIPES Entity (Center-Right)
    recipe_attrs = [
        ("id", "SERIAL", True, False),
        ("name", "VARCHAR(255)", False, False),
        ("description", "TEXT", False, False),
        ("instructions", "TEXT", False, False),
        ("image_url", "VARCHAR(500)", False, False),
        ("cuisine", "VARCHAR(100)", False, False),
        ("difficulty", "VARCHAR(50)", False, False),
        ("prep_time", "INT", False, False),
        ("cook_time", "INT", False, False),
        ("servings", "INT", False, False),
        ("diet_type", "VARCHAR(50)", False, False),
        ("rating", "FLOAT", False, False),
        ("popularity", "INT", False, False),
        ("source", "VARCHAR(50)", False, False),
        ("meal_type", "VARCHAR(50)", False, False),
    ]
    draw_entity(7.7, 3.3, 3.4, 6.2, "RECIPES", "#B91C1C", recipe_attrs)

    # 7. RECIPE_INGREDIENTS Entity (Bottom Center-Right)
    ri_attrs = [
        ("id", "SERIAL", True, False),
        ("recipe_id", "INT", False, True),
        ("ingredient_id", "INT", False, True),
        ("quantity", "FLOAT", False, False),
        ("unit", "VARCHAR(50)", False, False),
    ]
    draw_entity(7.7, 0.6, 3.4, 2.2, "RECIPE_INGREDIENTS", "#15803D", ri_attrs)

    # 8. INGREDIENTS Entity (Far Right Middle)
    ing_attrs = [
        ("id", "SERIAL", True, False),
        ("name", "VARCHAR(100) UQ", False, False),
    ]
    draw_entity(11.7, 4.4, 3.2, 1.8, "INGREDIENTS", "#C2410C", ing_attrs)

    # 9. INGREDIENT_SYNONYMS Entity (Far Right Top)
    syn_attrs = [
        ("id", "SERIAL", True, False),
        ("synonym_name", "VARCHAR(100) UQ", False, False),
        ("canonical_id", "INT", False, True),
    ]
    draw_entity(11.7, 7.3, 3.2, 2.2, "INGREDIENT_SYNONYMS", "#B45309", syn_attrs)

    # --- CONNECTORS WITH WHITE PILL BADGES ---
    def add_badge(x, y, text, color):
        ax.text(x, y, text, fontsize=8, fontweight='bold', color=color,
                ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, lw=1.2, zorder=4))

    # 1. Users <-> User_Preferences (1 to 0..1)
    ax.plot([2.2, 2.2], [4.6, 3.9], color="#0D9488", lw=2, zorder=2)
    add_badge(2.2, 4.35, "1", "#0D9488")
    add_badge(2.2, 4.05, "0..1", "#0D9488")

    # 2. Users <-> Favorites (1 to N)
    ax.plot([3.8, 4.3], [8.55, 8.55], color="#7C3AED", lw=2, zorder=2)
    add_badge(3.93, 8.55, "1", "#7C3AED")
    add_badge(4.17, 8.55, "N", "#7C3AED")

    # 3. Favorites <-> Recipes (N to 1)
    ax.plot([7.1, 7.7], [8.55, 8.55], color="#7C3AED", lw=2, zorder=2)
    add_badge(7.23, 8.55, "N", "#7C3AED")
    add_badge(7.57, 8.55, "1", "#7C3AED")

    # 4. Users <-> History (1 to N)
    ax.plot([3.8, 4.3], [5.9, 5.9], color="#8B5CF6", lw=2, zorder=2)
    add_badge(3.93, 5.9, "1", "#8B5CF6")
    add_badge(4.17, 5.9, "N", "#8B5CF6")

    # 5. History <-> Recipes (N to 1)
    ax.plot([7.1, 7.7], [5.9, 5.9], color="#8B5CF6", lw=2, zorder=2)
    add_badge(7.23, 5.9, "N", "#8B5CF6")
    add_badge(7.57, 5.9, "1", "#8B5CF6")

    # 6. Recipes <-> Recipe_Ingredients (1 to N)
    ax.plot([9.4, 9.4], [3.3, 2.8], color="#15803D", lw=2, zorder=2)
    add_badge(9.4, 3.16, "1", "#B91C1C")
    add_badge(9.4, 2.94, "N", "#15803D")

    # 7. Ingredients <-> Recipe_Ingredients (1 to N)
    ax.plot([11.7, 11.4, 11.4, 11.1], [5.3, 5.3, 1.7, 1.7], color="#C2410C", lw=2, zorder=2)
    add_badge(11.55, 5.3, "1", "#C2410C")
    add_badge(11.25, 1.7, "N", "#15803D")

    # 8. Ingredients <-> Ingredient_Synonyms (1 to N)
    ax.plot([13.3, 13.3], [6.2, 7.3], color="#B45309", lw=2, zorder=2)
    add_badge(13.3, 6.45, "1", "#C2410C")
    add_badge(13.3, 7.05, "N", "#B45309")

    # 9. OTP_VERIFICATIONS security link to USERS (Dashed relationship annotation)
    ax.annotate("", xy=(3.8, 5.0), xytext=(4.3, 2.5),
                arrowprops=dict(arrowstyle="->", lw=1.4, color="#64748B", linestyle=":",
                                connectionstyle="arc3,rad=-0.15"))
    ax.text(4.25, 3.95, "verifies target\n(email/phone)", fontsize=7.2, color='#475569', 
            ha='center', va='center', style='italic',
            bbox=dict(boxstyle="round,pad=0.2", fc="#F1F5F9", ec="#CBD5E1", lw=0.8))

    # Legend / Key
    legend_box = patches.FancyBboxPatch((0.6, 0.12), 14.3, 0.42, boxstyle="round,pad=0.04", 
                                        fc='#F1F5F9', ec='#CBD5E1', lw=1)
    ax.add_patch(legend_box)
    legend_text = "Legend:   PK = Primary Key  |  FK = Foreign Key  |  UQ = Unique Index Constraint  |  1:N = One-to-Many  |  1:1 = One-to-One  |  N:M = Many-to-Many Associative"
    ax.text(7.75, 0.33, legend_text, ha='center', va='center', fontsize=8.2, color='#334155', fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_6_er_diagram.png")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print("Saved:", path)

# ==============================================================================
# 6. Performance Evaluation Charts
# ==============================================================================
def draw_performance_benchmarks():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)
    fig.patch.set_facecolor('#F8F9FA')

    # Chart 1: Gemini Model Latency
    models = ['3.1-flash-lite\n(Optimized)', '3.6-flash\n(Fallback 1)', '3-flash-preview\n(Fallback 2)', 'flash-lite-latest\n(Previous/Failed)', '3.5-flash-lite\n(Previous/Failed)']
    times = [2.32, 3.85, 2.94, 30.0, 30.0]
    colors = ['#38A169', '#38A169', '#38A169', '#E53E3E', '#E53E3E']

    bars = ax1.bar(models, times, color=colors, width=0.55, edgecolor='#2D3748', lw=1)
    ax1.set_ylabel('Inference Execution Time (Seconds)', fontsize=9.5, fontweight='bold')
    ax1.set_title('Gemini AI Vision Model Response Latency', fontsize=10.5, fontweight='bold', pad=10)
    ax1.set_ylim(0, 35)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 0.8, f"{h:.1f}s", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    # Chart 2: Database Query Time
    strategies = ['Naive Join (3,300+ Recipes)\n[Unoptimized]', 'SQL Pre-filter (150 Candidates)\n[Optimized]']
    db_times = [82.7, 1.15]
    db_colors = ['#E53E3E', '#3182CE']

    bars2 = ax2.bar(strategies, db_times, color=db_colors, width=0.45, edgecolor='#2D3748', lw=1)
    ax2.set_ylabel('Query & Scoring Response Time (Seconds)', fontsize=9.5, fontweight='bold')
    ax2.set_title('Recipe Recommendation Latency (5,900+ DB Records)', fontsize=10.5, fontweight='bold', pad=10)
    ax2.set_ylim(0, 95)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h + 1.5, f"{h:.2f}s", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, "fig7_1_performance_benchmark.png")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print("Saved:", path)

# ==============================================================================
# 5b. Figure 4.5: UML Sequence Diagram
# ==============================================================================
def draw_sequence_diagram():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    ax.text(5.5, 7.1, "Figure 4.5: UML Sequence Diagram: Camera Capture to Recipe Recommendation", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1A202C')

    lifelines = [
        ("User", 1.0, "#4A5568"),
        ("Flutter Client", 2.8, "#2B6CB0"),
        ("FastAPI Backend", 4.8, "#2F855A"),
        ("Gemini AI API", 6.8, "#805AD5"),
        ("PostgreSQL DB", 8.6, "#D69E2E"),
        ("YouTube API", 10.2, "#E53E3E")
    ]

    for name, x, color in lifelines:
        box = patches.FancyBboxPatch((x - 0.7, 6.2), 1.4, 0.5, boxstyle="round,pad=0.08", fc=color, ec=color)
        ax.add_patch(box)
        ax.text(x, 6.45, name, ha='center', va='center', color='white', fontweight='bold', fontsize=8.5)
        ax.plot([x, x], [0.6, 6.2], linestyle='--', color='#A0AEC0', lw=1.2)

    messages = [
        (1.0, 2.8, 5.7, "1. Captures photo / selects pantry items", True, "#2D3748"),
        (2.8, 4.8, 5.2, "2. POST /api/ingredients/detect", True, "#2B6CB0"),
        (4.8, 6.8, 4.7, "3. generate_content(prompt, img) [10s timeout]", True, "#805AD5"),
        (6.8, 4.8, 4.2, "4. Structured JSON [ingredients: [...]]", False, "#805AD5"),
        (4.8, 2.8, 3.7, "5. Return detected items & confidences", False, "#2F855A"),
        (2.8, 1.0, 3.3, "6. Displays items, user adjusts filters", False, "#2B6CB0"),
        (1.0, 2.8, 2.9, "7. Confirms & taps 'Find Recipes'", True, "#2D3748"),
        (2.8, 4.8, 2.5, "8. POST /api/recipes/recommend (basket_use)", True, "#2B6CB0"),
        (4.8, 8.6, 2.1, "9. SQL Subquery match_count (LIMIT 150)", True, "#D69E2E"),
        (8.6, 4.8, 1.7, "10. Top 150 Recipe records returned (<0.2s)", False, "#D69E2E"),
        (4.8, 10.2, 1.3, "11. Fetch sanitized video tutorials", True, "#E53E3E"),
        (10.2, 4.8, 1.0, "12. Top cooking videos", False, "#E53E3E"),
        (4.8, 2.8, 0.75, "13. Return Top 20 Ranked Recipes + Videos", False, "#2F855A")
    ]

    for x1, x2, y, label, is_forward, color in messages:
        ls = '-' if is_forward else '--'
        arr = "->" if is_forward else "->"
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", lw=1.3, color=color, linestyle=ls))
        mid_x = (x1 + x2) / 2.0
        ax.text(mid_x, y + 0.1, label, ha='center', va='bottom', fontsize=7.2, color='#2D3748', fontweight='bold' if is_forward else 'normal')

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_5_sequence_diagram.png")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()
    print("Saved:", path)

if __name__ == "__main__":
    draw_system_architecture()
    draw_dfd_level_0()
    draw_dfd_level_1()
    draw_uml_use_case()
    draw_sequence_diagram()
    draw_er_diagram()
    draw_performance_benchmarks()
    print("All diagrams generated successfully!")
