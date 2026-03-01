"""
backend/demo.py
---------------
Full pipeline demo — runs all 5 agents with realistic mock data.
No API keys required. Safe for client presentations.

Usage:
    cd /home/shawn/Eric_Frank
    python -m backend.demo
"""
from __future__ import annotations

import time
import textwrap


# ---------------------------------------------------------------------------
# Terminal color helpers
# ---------------------------------------------------------------------------

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
GREY   = "\033[90m"
WHITE  = "\033[97m"
BG_DARK = "\033[40m"


def header(title: str) -> None:
    width = 62
    print()
    print(f"{BOLD}{CYAN}{'━' * width}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'━' * width}{RESET}")


def step(label: str, value: str = "", color: str = GREEN) -> None:
    print(f"  {color}{BOLD}{label}{RESET}  {WHITE}{value}{RESET}")


def info(text: str) -> None:
    print(f"  {GREY}{text}{RESET}")


def divider() -> None:
    print(f"  {GREY}{'─' * 56}{RESET}")


def pause(seconds: float = 0.8) -> None:
    time.sleep(seconds)


def box(title: str, content: str, color: str = WHITE) -> None:
    lines = textwrap.wrap(content, width=54)
    print(f"\n  {BOLD}{color}┌─ {title} {'─' * max(0, 50 - len(title))}┐{RESET}")
    for line in lines:
        print(f"  {color}│  {line:<54}│{RESET}")
    print(f"  {color}└{'─' * 58}┘{RESET}\n")


# ---------------------------------------------------------------------------
# Mock data — realistic LED industry demo data
# ---------------------------------------------------------------------------

MOCK_LEADS = [
    {"company": "Lumex Industrial Lighting GmbH",  "url": "lumex-industrial.de",      "country": "🇩🇪 Germany"},
    {"company": "NordicLight Distribution AB",      "url": "nordiclight.se",           "country": "🇸🇪 Sweden"},
    {"company": "Pacific Electrical Wholesale Co.", "url": "pacificelectrical.com.au", "country": "🇦🇺 Australia"},
    {"company": "BrightPath Lighting Solutions Ltd","url": "brightpath-lighting.co.uk","country": "🇬🇧 UK"},
    {"company": "AlphaVolt Energy Partners",        "url": "alphavolt.ca",             "country": "🇨🇦 Canada"},
]

MOCK_CONTACTS = {
    "lumex-industrial.de": {
        "name":    "Klaus Bauer",
        "title":   "Head of Procurement",
        "email":   "k.bauer@lumex-industrial.de",
        "context": (
            "Major DACH industrial LED distributor. Recently expanded into smart "
            "warehouse lighting. Actively sourcing new OEM suppliers to meet growing "
            "demand for high-bay and panel fixtures."
        ),
    },
    "nordiclight.se": {
        "name":    "Anna Lindqvist",
        "title":   "Purchasing Manager",
        "email":   "anna.lindqvist@nordiclight.se",
        "context": (
            "Serves Scandinavian retail and hospitality with eco-certified LEDs. "
            "Strict quality standards, current focus on dimmable LED strips and panels. "
            "Prefers ENEC/RoHS certified products."
        ),
    },
    "pacificelectrical.com.au": {
        "name":    "James Thornton",
        "title":   "General Manager",
        "email":   "j.thornton@pacificelectrical.com.au",
        "context": (
            "Top Australian electrical wholesaler with 12 branches across NSW & VIC. "
            "Supplies lighting to commercial contractors. Looking for competitive pricing "
            "on high-bay LED fixtures for large infrastructure projects."
        ),
    },
}

MOCK_COPY = {
    "lumex-industrial.de": {
        "subject": "30% faster LED supply for Lumex's warehouse projects?",
        "email": (
            "Hi Klaus,\n\n"
            "I noticed Lumex recently expanded into smart warehouse lighting — impressive "
            "move given the surge in German logistics infrastructure investment.\n\n"
            "We manufacture ISO 9001-certified LED high-bay fixtures with a 30% shorter "
            "lead time than market average (15 days vs. 21+). Several DACH distributors "
            "already use us to win time-sensitive tenders.\n\n"
            "Would a 15-minute call this week work to see if there's a fit?\n\n"
            "Best regards,\nSales Team"
        ),
        "whatsapp": (
            "Hi Klaus! Saw Lumex is expanding into smart warehouse lighting — "
            "we make industrial LEDs with 30% faster delivery. Worth a quick chat? 💡"
        ),
    },
    "nordiclight.se": {
        "subject": "ENEC-certified dimmable LEDs for NordicLight's new line?",
        "email": (
            "Hi Anna,\n\n"
            "NordicLight's focus on eco-certified products caught my eye — exactly "
            "the standard your Scandinavian hospitality clients demand.\n\n"
            "Our dimmable LED panel range carries CE, RoHS, and ENEC certification. "
            "We also offer private-label packaging under your own brand.\n\n"
            "Happy to send samples this week — would that be helpful?\n\n"
            "Best regards,\nSales Team"
        ),
        "whatsapp": (
            "Hi Anna! We make ENEC-certified dimmable LEDs that match NordicLight's "
            "eco standards. Can send samples this week — interested? 🌿"
        ),
    },
    "pacificelectrical.com.au": {
        "subject": "Bulk LED high-bay pricing for Pacific Electrical's projects?",
        "email": (
            "Hi James,\n\n"
            "Pacific Electrical's scale across NSW and VIC is impressive — especially "
            "the volume of commercial contractor work you handle.\n\n"
            "We supply LED high-bay fixtures at bulk pricing with 15-day delivery, "
            "ideal for large infrastructure tenders. Our fixtures come with 5-year "
            "warranty and local compliance certification.\n\n"
            "Could we schedule a quick call to discuss your upcoming project pipeline?\n\n"
            "Best regards,\nSales Team"
        ),
        "whatsapp": (
            "Hi James! We supply bulk LED high-bays with 15-day delivery and 5yr warranty — "
            "great fit for your contractor projects. Quick chat? ⚡"
        ),
    },
}

MOCK_SDR_REPLIES = [
    {
        "company": "Lumex Industrial GmbH",
        "reply":   "Hi, yes we'd like to get a quote and schedule a call this week.",
        "intent":  "A",
        "label":   "HIGH INTENT",
        "color":   GREEN,
        "action":  "Calendly link sent + Feishu team alert triggered",
    },
    {
        "company": "NordicLight Distribution AB",
        "reply":   "Thanks for reaching out. We're reviewing suppliers next quarter — follow up then.",
        "intent":  "B",
        "label":   "NURTURE",
        "color":   YELLOW,
        "action":  "Tagged for Q2 follow-up sequence",
    },
    {
        "company": "Pacific Electrical Wholesale",
        "reply":   "Please remove me from your list. Not interested.",
        "intent":  "C",
        "label":   "REJECTED",
        "color":   RED,
        "action":  "Lead blacklisted — removed from pipeline",
    },
]


# ---------------------------------------------------------------------------
# Demo runner
# ---------------------------------------------------------------------------

def run_demo() -> None:

    # Title
    print()
    print(f"{BOLD}{BG_DARK}{CYAN}{'═' * 62}{RESET}")
    print(f"{BOLD}{BG_DARK}{CYAN}   B2B AI Outreach Pipeline — Live Demo{' ' * 22}{RESET}")
    print(f"{BOLD}{BG_DARK}{CYAN}   Product: High-Precision Industrial LED Fixtures{' ' * 12}{RESET}")
    print(f"{BOLD}{BG_DARK}{CYAN}{'═' * 62}{RESET}")
    print()
    info("  All 5 AI Agents will run in sequence.")
    info("  Watch how the system finds, enriches, and reaches out to leads.")
    pause(1.5)

    # -----------------------------------------------------------------------
    # AGENT 1 — Scout
    # -----------------------------------------------------------------------
    header("AGENT 1 / 5   Scout — Google Search & Lead Discovery")
    info("Searching Google for B2B distributors of LED fixtures...")
    info("Search query: Find B2B distributors for \"LED lighting\",")
    info("              exclude Alibaba, Made-in-China, -site:competitors")
    pause(1.2)
    print()

    for i, lead in enumerate(MOCK_LEADS, 1):
        pause(0.4)
        print(f"  {GREEN}✓{RESET}  [{i}] {BOLD}{lead['company']}{RESET}")
        print(f"       {GREY}→ {lead['url']}   {lead['country']}{RESET}")

    print()
    step("Result:", f"{len(MOCK_LEADS)} qualified leads found", GREEN)
    info("Blacklisted domains filtered: alibaba.com, made-in-china.com ...")
    info("All leads saved to DB with status: Scouted")
    pause(1.0)

    # -----------------------------------------------------------------------
    # AGENT 2 — Miner
    # -----------------------------------------------------------------------
    header("AGENT 2 / 5   Miner — Website Scrape & Contact Enrichment")
    info("Scraping each company website + querying Apollo.io for decision makers...")
    pause(0.8)
    print()

    for domain, contact in MOCK_CONTACTS.items():
        company = next((l["company"] for l in MOCK_LEADS if l["url"] == domain), domain)
        print(f"  {CYAN}▶  {BOLD}{company}{RESET}")
        pause(0.5)
        step("  Contact :", f"{contact['name']} — {contact['title']}")
        step("  Email   :", contact["email"])
        box("Company Intel", contact["context"], GREY)
        pause(0.3)

    step("Result:", f"{len(MOCK_CONTACTS)} leads fully enriched", GREEN)
    info("Status updated to: Mined")
    pause(1.0)

    # -----------------------------------------------------------------------
    # AGENT 3 — Writer
    # -----------------------------------------------------------------------
    header("AGENT 3 / 5   Writer — AI Personalised Copy (Claude 3.5 Sonnet)")
    info("Generating personalised cold email + WhatsApp message per lead...")
    pause(0.8)
    print()

    for domain, copy in MOCK_COPY.items():
        company = next((l["company"] for l in MOCK_LEADS if l["url"] == domain), domain)
        contact = MOCK_CONTACTS.get(domain, {})
        print(f"  {CYAN}▶  {BOLD}{company}{RESET}  ({contact.get('name', '')})")
        pause(0.6)
        step("  Subject  :", copy["subject"], YELLOW)
        print()
        for line in copy["email"].splitlines():
            print(f"  {GREY}│{RESET}  {line}")
        print()
        print(f"  {YELLOW}WhatsApp:{RESET}  {copy['whatsapp']}")
        divider()
        pause(0.4)

    step("Result:", f"{len(MOCK_COPY)} drafts generated", GREEN)
    info("Status updated to: Drafted  |  is_approved = False")
    pause(1.0)

    # -----------------------------------------------------------------------
    # HUMAN REVIEW
    # -----------------------------------------------------------------------
    header("⏸  HUMAN REVIEW — Waiting for Manager Approval")
    print()
    print(f"  {YELLOW}{BOLD}  Pipeline paused here.{RESET}")
    print(f"  {WHITE}  Manager reviews the generated copy in the dashboard.{RESET}")
    print(f"  {WHITE}  Call POST /approve_draft to resume.{RESET}")
    print()
    info("  [ Simulating manager approval in 2 seconds... ]")
    pause(2.0)
    print(f"  {GREEN}{BOLD}✓  Draft approved by manager. Pipeline resuming...{RESET}")
    pause(0.8)

    # -----------------------------------------------------------------------
    # AGENT 4 — Outreach
    # -----------------------------------------------------------------------
    header("AGENT 4 / 5   Outreach — Email + WhatsApp Delivery")
    info("Sending approved messages via Instantly (Email) and Wati (WhatsApp)...")
    info("Anti-ban delay: 45–120s between sends (simulated here as 0.5s)")
    print()

    for domain, copy in MOCK_COPY.items():
        company = next((l["company"] for l in MOCK_LEADS if l["url"] == domain), domain)
        contact = MOCK_CONTACTS.get(domain, {})
        pause(0.5)
        print(f"  {CYAN}▶  {BOLD}{company}{RESET}")
        step("  📧 Email    :", f"Sent to {contact.get('email', 'N/A')}   [Instantly API]", GREEN)
        step("  💬 WhatsApp :", f"Sent to +{domain[:3].upper()}-XXXXX   [Wati API]", GREEN)
        divider()

    print()
    step("Result:", f"{len(MOCK_COPY)} leads contacted (email + WhatsApp)", GREEN)
    info("Status updated to: Emailed / WhatsApped")
    info(f"Daily send counter updated. Limit: 50/day")
    pause(1.0)

    # -----------------------------------------------------------------------
    # AGENT 5 — SDR
    # -----------------------------------------------------------------------
    header("AGENT 5 / 5   SDR — Reply Intent Classification")
    info("Customer replies are coming in. Classifying each reply...")
    info("  A = High intent (quote/meeting/sample)")
    info("  B = Nurture (follow up later)")
    info("  C = Reject (unsubscribe / not interested)")
    print()
    pause(0.8)

    for reply_data in MOCK_SDR_REPLIES:
        pause(0.6)
        color = reply_data["color"]
        print(f"  {CYAN}▶  {BOLD}{reply_data['company']}{RESET}")
        print(f"  {GREY}   \"{reply_data['reply']}\"{RESET}")
        print()
        print(f"  {color}{BOLD}   → Intent: [{reply_data['intent']}] {reply_data['label']}{RESET}")
        print(f"  {WHITE}   → Action: {reply_data['action']}{RESET}")
        divider()

    pause(1.0)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print()
    print(f"{BOLD}{CYAN}{'═' * 62}{RESET}")
    print(f"{BOLD}{CYAN}   Pipeline Complete — Summary{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 62}{RESET}")
    print()
    step("  Leads Discovered  :", "5 companies", CYAN)
    step("  Leads Enriched    :", "3 with decision-maker contacts", CYAN)
    step("  Drafts Generated  :", "3 personalised emails + WhatsApp", CYAN)
    step("  Messages Sent     :", "3 via Email + WhatsApp", CYAN)
    step("  A (High Intent)   :", "1 — Calendly sent, team alerted", GREEN)
    step("  B (Nurture)       :", "1 — Tagged for Q2 follow-up", YELLOW)
    step("  C (Rejected)      :", "1 — Blacklisted, pipeline removed", RED)
    print()
    print(f"  {GREY}Full audit trail saved to PostgreSQL database.{RESET}")
    print(f"  {GREY}View all leads at: GET /leads{RESET}")
    print()
    print(f"{BOLD}{CYAN}{'═' * 62}{RESET}")
    print()


if __name__ == "__main__":
    run_demo()
