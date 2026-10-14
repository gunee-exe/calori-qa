"""Builds Calori_Test_Summary_Report.docx from the design, results and defect data."""
import datetime as dt
import json
import pathlib
from collections import Counter

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

import annotate
import defects as D
import design_requirements as R
import design_testcases as T
from docgen_helpers import Doc, INK

HERE = pathlib.Path(__file__).parent
Q = HERE.parent
OUTFILE = Q / "Calori_Test_Summary_Report.docx"
import sys
TOC_ENTRIES = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")) if len(sys.argv) > 1 else None

RES = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
TCS = T.TEST_CASES
TC_BY_ID = {t["id"]: t for t in TCS}
DEFS = D.DEFECTS
REQS = R.REQUIREMENTS
MOD = R.MODULES
OWNER = R.MODULE_OWNER
ROLL = {"Usman Ghani": "24f3000", "Faizan Ali": "24f3029"}
SOURCES = json.loads((Q / "test-data" / "food-images" / "SOURCES.json").read_text(encoding="utf-8"))

APP = "Calori"
VERSION = "1.0.0 (build 1), source commit 35e2473 (2 Sep 2026)"
REPORT_DATE = "11 October 2026"
_SHA1 = Q / "aut-35e2473/build/app/outputs/flutter-apk/app-release.apk.sha1"
APK_SHA1 = (_SHA1.read_text().strip() if _SHA1.exists()
            else __import__("hashlib").sha1((Q / "Calori-1.0.0+1-35e2473-release.apk").read_bytes()).hexdigest())
START = dt.datetime.strptime((Q / "work/start-time.txt").read_text().strip(), "%Y-%m-%d %H:%M:%S")
END = dt.datetime.strptime((Q / "work/end-time.txt").read_text().strip(), "%Y-%m-%d %H:%M:%S")
PAID = int((Q / "work/paid_calls.txt").read_text().strip())

TECH_NAMES = {"EP": "Equivalence Partitioning", "BVA": "Boundary Value Analysis", "DT": "Decision Table",
              "ST": "State Transition", "EG": "Error Guessing"}


def fmt_date(s):
    return dt.datetime.strptime(s, "%Y-%m-%d").strftime("%d-%b-%Y")


def status(tid):
    return RES[tid]["status"]


def tester(t):
    return OWNER[t["module"]]


def techs(t):
    out = []
    for k in TECH_NAMES:
        if k in t["technique"].replace("(", " ").split() or t["technique"].startswith(k):
            out.append(k)
    return out


counts = Counter(status(t["id"]) for t in TCS)
N = len(TCS)
PASS, FAIL = counts.get("Pass", 0), counts.get("Fail", 0)
BLOCKED, NOTEX = counts.get("Blocked", 0), counts.get("Not Executed", 0)
EXECUTED = N - NOTEX
PASS_PCT = PASS / EXECUTED * 100
SEV = Counter(x["severity"] for x in DEFS)
PRI = Counter(x["priority"] for x in DEFS)
exec_hours = (END - START).total_seconds() / 3600

doc = Doc()
d = doc.d
d.core_properties.title = "Calori – Test Summary Report"
d.core_properties.author = "Usman Ghani; Faizan Ali"
d.core_properties.subject = "Software Quality Engineering – Assignment 2"

sec0 = d.sections[0]
sec0.different_first_page_header_footer = True
doc.header(sec0, "Calori 1.0.0 – Test Summary Report")
doc.footer(sec0, "Software Quality Engineering – Assignment 2")

# ===================================================================== title
for _ in range(4):
    doc.p("")
doc.p("Software Quality Engineering – Assignment 2", size=12, align="center", color=RGBColor(0x52, 0x51, 0x4E))
doc.p("Manual Functional Testing and Test Reporting", size=12, align="center", color=RGBColor(0x52, 0x51, 0x4E), after=28)
doc.p("Test Summary Report", bold=True, size=30, align="center", color=INK, after=4)
doc.p("Calori – calorie and macro tracker for Android", size=15, align="center", after=4)
doc.p(f"Version under test: {VERSION}", size=11, align="center", after=36)
doc.table(["Group member", "Roll number", "Role"],
          [["Usman Ghani", "24f3000", "Test lead / test engineer"], ["Faizan Ali", "24f3029", "Test engineer"]],
          [6.0, 4.0, 6.0], size=11, zebra=False)
doc.p("")
doc.table(["Course", "Instructors", "Report date"],
          [["Software Quality Engineering", "Mr. Fraz Zaheer, Mr. Talha Dar", REPORT_DATE]], [5.5, 6.0, 4.5], size=11, zebra=False)
doc.page_break()

# ========================================================== document control
doc.p("Document Control", bold=True, size=16, color=INK, after=8)
doc.table(["Item", "Detail"], [
    ["Document", "Test Summary Report (with test plan, RTM, test cases, defect log and evidence as appendices)"],
    ["Application", f"{APP} – Android calorie and macro tracker (open-source Flutter project)"],
    ["Version under test", VERSION],
    ["Build", f"Release APK built from source, SHA-1 {APK_SHA1}"],
    ["Prepared by", "Usman Ghani (24f3000), Faizan Ali (24f3029)"],
    ["Prepared for", "Mr. Fraz Zaheer, Mr. Talha Dar – Software Quality Engineering"],
    ["Status", "Final – for submission"],
], [4.0, 13.0], size=10, bold_first_col=True)
doc.caption("Table", "Document information")
doc.p("Version history", bold=True, after=4)
doc.table(["Version", "Date", "Author", "Change"], [
    ["0.1", "11-Oct-2026", "Usman Ghani", "Test plan, scope and requirement list (FR-001 – FR-046)"],
    ["0.2", "11-Oct-2026", "Faizan Ali", f"Test case design ({N - 1} cases), RTM, expected values from the formula oracle"],
    ["0.3", "11-Oct-2026", "Both", f"Execution results for all cases; TC-077 added during execution; {len(DEFS)} defects logged"],
    ["1.0", "11-Oct-2026", "Both", "Charts, analysis, recommendations and sign-off – final"],
], [1.6, 2.6, 2.8, 10.0], size=10)
doc.caption("Table", "Version history")
doc.p("Abbreviations", bold=True, after=4)
doc.table(["Term", "Meaning"], [
    ["AUT", "Application under test"], ["FR", "Functional requirement"], ["TC", "Test case"], ["DEF", "Defect"],
    ["RTM", "Requirement traceability matrix"], ["EP / BVA / DT / ST / EG",
     "Equivalence partitioning / boundary value analysis / decision table / state transition / error guessing"],
    ["BMI", "Body-mass index (kg ÷ m²)"], ["TDEE", "Total daily energy expenditure (maintenance calories)"],
    ["kcal", "Kilocalories"], ["UC-xx", "Use case from the project's 04-use-cases.md"],
], [4.0, 13.0], size=10)
doc.caption("Table", "Abbreviations")
doc.page_break()
doc.p("Table of Contents", bold=True, size=16, color=INK, after=8)
doc.toc(TOC_ENTRIES)
doc.page_break()

# ========================================================= 1. executive summary
doc.h("1. Executive Summary", 1)
doc.p(f"This report presents the results of manual functional testing of **Calori**, an Android calorie and macro "
      f"tracker, at version 1.0.0 (build 1), the source state of commit 35e2473 dated 2 September 2026. A two-person "
      f"QA team tested a release build on an Android 16 emulator on {REPORT_DATE}, including the optional "
      f"photo-estimate service.")
doc.p(f"We tested eight modules – onboarding, the goal and safety rules, manual food logging, the day view, the "
      f"calendar, goal management, photo logging and navigation – against {len(REQS)} functional requirements derived "
      f"from the project's use cases. All {N} test cases were executed: **{PASS} passed ({PASS_PCT:.1f}%) and {FAIL} "
      f"failed**, none were blocked. We logged **{len(DEFS)} defects**: {SEV['Critical']} Critical, {SEV['Major']} "
      f"Major, {SEV['Minor']} Minor and {SEV['Trivial']} Trivial.")
doc.p("**What works well.** Calorie and macro targets matched the published formula exactly in every scenario we "
      "calculated independently; the safety refusals and corrections appear inline with clear wording; food search is "
      "fast, works offline and says clearly when nothing matches; the photo path answers 'no food' and 'no connection' honestly "
      "and keeps the photo for a retry; a repeated meal gives identical numbers.")
doc.p("**Key findings.**", after=2)
doc.bullets([
    "Underweight users cannot finish setting up: both alternatives the app offers them lead to a loading screen that "
    "never ends (DEF-06, Critical).",
    "The under-18 stop – the app's only hard safety block – is bypassed by closing and reopening the app (DEF-02).",
    "Saved goals are unreliable: switching kg/lb erases the goal date and a hand-set target (DEF-23); the Goal screen "
    "sets a target up to 220 kcal away from the rate the user chose (DEF-24); changing the goal rewrites past days' "
    "results (DEF-22) and leaves Home's progress ring stale (DEF-21).",
    "After a food is added by hand, its card stays stuck on 'Saving…' and cannot be used again (DEF-11).",
    "In the photo flow, proposed portions cannot be corrected before saving (DEF-27), typed details are ignored "
    "for gallery photos (DEF-30) and the camera's Close button cannot be tapped (DEF-26).",
])
doc.p("**Quality statement and recommendation: Not ready for release.** One Critical defect blocks an entire group "
      f"of users, and the {PRI['High']} High-priority defects undermine the two things Calori exists to do – set a safe "
      "target and record intake accurately. Release should be reconsidered once the High-priority defects are fixed "
      "and the failed test cases pass on re-test (Section 6).")

# ============================================================ 2. introduction
doc.h("2. Introduction", 1)
doc.h("2.1 Purpose of the report", 2)
doc.p("This report records what was tested in Calori, how it was tested, what was found, and whether the application "
      "is functionally fit to release. It is written so that a non-technical reader can follow the summary sections, "
      "while the appendices hold the full test plan, traceability, test cases, defect reports and evidence for review.")
doc.h("2.2 Application overview", 2)
doc.p("Calori is an open-source Flutter application for Android that estimates a daily calorie and protein target "
      "and lets the user log what they eat. Its main parts are:")
doc.bullets([
    "**Onboarding and goal engine** – asks for sex, age, height, weight, target weight and activity, computes a target "
    "with the Mifflin-St Jeor equation, and applies safety rules (adults only, no target below BMI 18.5, at most 1 % of "
    "bodyweight per week, a calorie floor of 1,500 kcal for men and 1,200 kcal for women).",
    "**Manual logging** – an offline database of about 21,800 foods from eight national food tables, searchable in "
    "English and regional names, with household serving sizes.",
    "**Day view, calendar and goal screen** – progress against the target per day and per month, editing of logged "
    "meals, and changes to the goal with hand-set overrides.",
    "**Photo logging (optional)** – a meal photo is sent to the developer's own Cloudflare Worker, which asks a vision "
    "model for a list of foods; nothing is saved until the user confirms.",
])
doc.h("2.3 Version and environment under test", 2)
doc.table(["Item", "Value"], [
    ["Application / version", f"{APP} {VERSION}"],
    ["Build", f"flutter build apk --release with photo estimates configured; APK SHA-1 {APK_SHA1}"],
    ["Device", "Android Emulator, AVD 'finall' (sdk_gphone64_x86_64), Android 16 / API 36, 1080 × 2424 px at 420 dpi"],
    ["Photo service", "Developer's Cloudflare Worker (health check OK), model google/gemini-2.5-flash via OpenRouter"],
    ["Network", "Online; airplane mode for the offline cases (TC-070)"],
    ["Test date and time", f"{START:%d-%b-%Y}, {START:%H:%M}–{END:%H:%M} (local time)"],
], [4.2, 12.8], size=10, bold_first_col=True)
doc.caption("Table", "Version and environment under test")
doc.h("2.4 Modules and features tested", 2)
mod_rows = []
for m, name in MOD.items():
    feats = {
        "M1": "Sex, age, height and weight entry; unit toggles; under-18 stop; back navigation",
        "M2": "Target calculation, macro split, BMI refusals, rate and calorie-floor clamps, plan screen",
        "M3": "Food search, regional names, no-match handling, portion picker, add to log, recent foods",
        "M4": "Ring and totals, date strip, entry editor (meal type, portions, remove), delete and undo",
        "M5": "Month grid, month paging, day detail, month summary, history kept against old targets",
        "M6": "Goal steppers, rate, refusals, hand-set calories and protein, unit preferences, Sources",
        "M7": "Viewfinder, gallery photos, details hint, review and correction, save, no-food, offline, repeat meals",
        "M8": "Nav bar tabs, '+' and calendar buttons, Android Back",
    }[m]
    n_req = sum(1 for r in REQS if r[1] == m)
    n_tc = sum(1 for t in TCS if t["module"] == m)
    mod_rows.append([m, name, feats, str(n_req), str(n_tc), OWNER[m]])
doc.table(["ID", "Module", "Features covered", "FRs", "TCs", "Owner"], mod_rows, [1.0, 3.4, 7.6, 1.1, 1.1, 2.8], size=9,
          align_center_cols=(3, 4))
doc.caption("Table", "Modules and features tested")
doc.p("Out of scope by definition: all non-functional testing (performance, security, usability, compatibility, "
      "accessibility), unit and automated testing, iOS, and the internals of the Worker and of the food-database build "
      "tools. The full scope statement is in Appendix A.")

# ======================================================== 3. approach & strategy
doc.h("3. Test Approach and Strategy", 1)
doc.h("3.1 Overall approach", 2)
doc.p("Testing was requirements-based black-box testing. Requirements were derived from the project's twelve use "
      "cases, its README and statements the app makes on screen (Appendix B). Each test case was designed before "
      "execution with an expected result taken from the requirement. For calculations, expected values came from an "
      "independent re-implementation of the published formula (the 'oracle'), never from the app itself – for "
      "example, the reference profile (male, 30, 178 cm, 78 → 72 kg, moderately active) must give 2,160 kcal and "
      "140 g protein.")
doc.p("Every test case was executed by hand, one step at a time, on the emulator. Android's adb tool was used to "
      "send taps and text, to read the text shown on screen, to capture screenshots and to record screen video. "
      "Scripted test sessions were complemented by six time-boxed exploratory sessions (Appendix E), which found "
      f"{sum(1 for x in DEFS if x['found'][0].startswith('EXP'))} further defects and several usability observations.")
doc.h("3.2 Test design techniques", 2)
tech_count = Counter(k for t in TCS for k in techs(t))
doc.table(["Technique", "Test cases using it", "Example from this project"], [
    ["Equivalence Partitioning", str(tech_count["EP"]),
     "Valid metric and imperial units as separate input classes (TC-006, TC-010); regional versus English food "
     "names (TC-027); a meal photo versus a photo with no food (TC-069)."],
    ["Boundary Value Analysis", str(tech_count["BVA"]),
     "Age 17 / 18 and 119 (TC-003, TC-004); maintenance band at ±0.5 kg – 78.5 vs 78.6 kg (TC-022); calorie floor "
     "1,499 / 1,500 kcal (TC-058); month paging stops at the current month (TC-048)."],
    ["Decision Table", str(tech_count["DT"]),
     "The UC-02 safety rules as an eight-rule table (Table 7), one or more test cases per rule (TC-004, TC-013–TC-016, TC-018–TC-022, TC-077)."],
    ["State Transition", str(tech_count["ST"]),
     "Onboarding steps and their transitions, including restart and the refusal state (Table 8); entry "
     "life-cycle add → edit → delete (TC-033, TC-039, TC-044)."],
    ["Error Guessing", str(tech_count["EG"]),
     "Adding the same food twice (TC-034); restarting after the under-18 refusal (TC-013); taking the alternative "
     "offered to an underweight user (TC-077); switching units with a hand-set target (TC-061); losing the connection "
     "during photo analysis (TC-070)."],
], [3.6, 2.4, 11.0], size=9)
doc.caption("Table", "Test design techniques used, with examples")

dt_rows = [
    ["Age < 18", "Y", "N", "N", "N", "N", "N", "N", "N"],
    ["Current BMI < 18.5 and goal is to lose", "–", "Y", "N", "N", "N", "N", "N", "N"],
    ["Target BMI < 18.5", "–", "–", "Y", "Y", "N", "N", "N", "N"],
    ["Direction of goal", "–", "lose", "lose / keep", "gain", "lose / gain", "lose", "lose", "any"],
    ["Rate > 1 % of bodyweight per week", "–", "–", "–", "–", "Y", "–", "–", "N"],
    ["Target would fall below calorie floor", "–", "–", "–", "–", "–", "Y", "–", "N"],
    ["Maintenance (TDEE) ≤ floor", "–", "–", "–", "–", "–", "N", "Y", "N"],
    ["ACTION", "Block: refusal screen, no way on", "Refuse; offer maintain", "Refuse; offer maintain",
     "Refuse; offer healthy-weight gain", "Clamp rate; honest date", "Clamp to floor; later date", "Set to maintain",
     "Accept plan"],
    ["Test cases", "TC-004, TC-013", "TC-077", "TC-016", "TC-018", "TC-015, TC-019", "TC-020",
     "TC-021", "TC-014, TC-022"],
    ["Result", "Pass / Fail", "Fail", "Pass", "Fail", "Pass / Fail", "Pass", "Pass", "Pass"],
]
doc.table(["Condition / action", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"], dt_rows,
          [4.2] + [1.6] * 8, size=8, bold_first_col=True, align_center_cols=tuple(range(1, 9)))
doc.caption("Table", "Decision table for the onboarding safety rules (UC-02)")

st_rows = [
    ["Sex", "Choose Male / Female", "Age", "TC-002", status("TC-002")],
    ["Age", "Valid age ≥ 18, Continue", "Height & weight", "TC-003", status("TC-003")],
    ["Age", "Age < 18, Continue", "Blocked (refusal)", "TC-004", status("TC-004")],
    ["Blocked", "App restarted", "Blocked", "TC-013", status("TC-013")],
    ["Target", "Refused; 'Maintain instead'", "Activity → Plan (maintenance)", "TC-016", status("TC-016")],
    ["Target", "Underweight; alternative chosen", "Activity → Plan", "TC-018, TC-077", "Fail"],
    ["Plan", "Start tracking", "Home (profile saved)", "TC-025", status("TC-025")],
]
doc.table(["From state", "Event", "Expected next state", "Test case", "Result"], st_rows, [3.2, 4.6, 4.6, 2.6, 2.0],
          size=9, status_col=4)
doc.caption("Table", "State transition table for onboarding")
doc.h("3.3 How test cases were prioritised", 2)
doc.p("Each test case carries a priority (how soon it must run and be fixed if it fails) and a severity (how much harm "
      "a failure would do). Priority was set by risk:")
doc.bullets([
    "**High** – safety rules, calorie calculations, saving and deleting data, and the core logging paths. A failure "
    "here either harms the user or makes the diary wrong.",
    "**Medium** – input validation, edge cases, secondary displays such as the calendar and Recent foods.",
    "**Low** – cosmetic or informational behaviour (e.g. the Sources screen).",
])
doc.p("Because many cases share set-up state (a saved profile, logged meals), execution followed module order. "
      "Priority was then used to rank defects and to decide what blocks release.")
doc.h("3.4 Roles and responsibilities", 2)
doc.table(["Member", "Roll no.", "Role", "Responsibilities"], [
    ["Usman Ghani", "24f3000", "Test lead",
     "Test plan and scope; environment set-up (APK build, emulator, test images); design and execution of M1 Onboarding, "
     "M2 Goal engine and M7 Photo logging; exploratory sessions EXP-01 and EXP-05; compiling the report."],
    ["Faizan Ali", "24f3029", "Test engineer",
     "Requirement analysis and RTM; design and execution of M3 Manual logging, M4 Day view, M5 Calendar, M6 Goal "
     "management and M8 Navigation; exploratory sessions EXP-02, EXP-03, EXP-04, EXP-06; defect-log consolidation and "
     "report review."],
], [3.0, 2.0, 2.6, 9.4], size=9)
doc.caption("Table", "Roles and responsibilities")
doc.h("3.5 Tools used", 2)
doc.table(["Tool", "Used for"], [
    ["Flutter SDK + Gradle", "Building the release APK from the 35e2473 source"],
    ["Android Emulator (Android 16)", "Running the application under test"],
    ["Android Debug Bridge (adb)", "Taps and text input, reading on-screen text, screenshots (screencap), screen video "
                                   "(screenrecord), airplane mode, force-stop and data reset between scenarios"],
    ["Python (Pillow, matplotlib, python-docx)", "Results log, highlight boxes on screenshots, charts, this document"],
    ["Formula oracle (oracle.py)", "Independent expected values for every calculation test"],
    ["Wikimedia Commons", "Openly licensed meal photos used as photo test data (Appendix A.11)"],
    ["Microsoft Word / LibreOffice", "Report format (.docx) and page-layout checks"],
], [5.0, 12.0], size=9)
doc.caption("Table", "Tools used")

# ===================================================== 4. execution summary
doc.h("4. Test Execution Summary", 1)
doc.h("4.1 Overall metrics", 2)
doc.table(["Metric", "Value"], [
    ["Total test cases designed", f"{N} ({N - 1} before execution + 1 added during execution: TC-077)"],
    ["Test cases executed", f"{EXECUTED}"],
    ["Passed", f"{PASS}"],
    ["Failed", f"{FAIL}"],
    ["Blocked", f"{BLOCKED}"],
    ["Not executed", f"{NOTEX}"],
    ["Pass percentage", f"{PASS_PCT:.1f}% ({PASS} of {EXECUTED})"],
    ["Execution effort (hours)", f"{exec_hours:.1f} h on {START:%d-%b-%Y} ({START:%H:%M}–{END:%H:%M}), "
                                 f"including 0.25 h build and set-up"],
    ["Requirements covered", f"{len(REQS)} of {len(REQS)} (100%)"],
    ["Defects logged", f"{len(DEFS)} ({sum(1 for x in DEFS if x['found'][0].startswith('EXP'))} from exploratory sessions)"],
    ["Paid photo-analysis calls used", f"{PAID} (limit agreed with the project owner: 20)"],
], [6.0, 11.0], size=10, bold_first_col=True)
doc.caption("Table", "Test execution metrics")
doc.image(HERE / "charts/pass_fail.png", 11.5, f"Overall pass/fail result of the {EXECUTED} executed test cases")
doc.h("4.2 Module-wise breakdown", 2)
rows = []
for m in MOD:
    ts = [t for t in TCS if t["module"] == m]
    p = sum(1 for t in ts if status(t["id"]) == "Pass")
    f = sum(1 for t in ts if status(t["id"]) == "Fail")
    nd = sum(1 for x in DEFS if x["module"] == m)
    rows.append([f"{m} {MOD[m]}", OWNER[m], str(len(ts)), str(p), str(f), "0", f"{p / len(ts) * 100:.0f}%", str(nd)])
rows.append(["Total", "", str(N), str(PASS), str(FAIL), str(BLOCKED), f"{PASS_PCT:.0f}%", str(len(DEFS))])
doc.table(["Module", "Tester", "TCs", "Pass", "Fail", "Blocked", "Pass %", "Defects"], rows,
          [5.4, 2.8, 1.3, 1.3, 1.3, 1.5, 1.6, 1.8], size=9, align_center_cols=(2, 3, 4, 5, 6, 7))
doc.caption("Table", "Results by module")
doc.image(HERE / "charts/module_results.png", 16.0, "Passed and failed test cases per module")
doc.h("4.3 Requirement coverage", 2)
req_status = {}
for rid, *_ in REQS:
    linked = [t["id"] for t in TCS if rid in t["reqs"]]
    req_status[rid] = "Pass" if all(status(x) == "Pass" for x in linked) else "Fail"
rp = sum(1 for v in req_status.values() if v == "Pass")
doc.p(f"All {len(REQS)} requirements are covered by at least one test case. {rp} requirements are fully met (every "
      f"linked case passed) and {len(REQS) - rp} have at least one failing case. The complete traceability matrix is "
      f"in Appendix B.")
doc.h("4.4 Notes on execution", 2)
doc.bullets([
    "TC-077 was added during execution, when exploring the refused loss goal of an underweight user showed that "
    "'Maintain instead' leads to an endless spinner; it is designed, traced and reported like every other case.",
    "Two test cases had their test data adjusted to match the product: the quantity stepper moves in 0.5 steps, so "
    "TC-032 compares 1 with 1.5 servings; TC-066 ran on the review screen of TC-064 so that no extra paid "
    "photo call was needed.",
    "Calculation cases were checked against the oracle; all matched exactly except where a defect is reported "
    "(TC-056 / DEF-24).",
    "Each onboarding scenario started from cleared app data so that earlier answers could not influence the result.",
])

# ====================================================== 5. defect summary
doc.h("5. Defect Summary", 1)
doc.p(f"{len(DEFS)} defects were logged, each reproduced on the device with screenshot evidence (two also have screen "
      f"video). All are **Open**: this cycle tested a fixed historical build, so no fixes were delivered during testing.")
sev_order = ["Critical", "Major", "Minor", "Trivial"]
pri_order = ["High", "Medium", "Low"]
doc.table(["Severity", "Count", "Meaning"], [
    ["Critical", str(SEV["Critical"]), "Blocks a core flow for a group of users with no workaround"],
    ["Major", str(SEV["Major"]), "Wrong result, data loss or a broken feature; a workaround may exist"],
    ["Minor", str(SEV["Minor"]), "Incorrect behaviour in validation, wording or a secondary feature"],
    ["Trivial", str(SEV["Trivial"]), "Cosmetic"],
    ["Total", str(len(DEFS)), ""],
], [3.0, 2.0, 12.0], size=9, align_center_cols=(1,))
doc.caption("Table", "Defects by severity")
doc.table(["Priority", "Count", "Status", "Count"], [
    ["High", str(PRI["High"]), "Open", str(len(DEFS))],
    ["Medium", str(PRI["Medium"]), "Fixed", "0"],
    ["Low", str(PRI["Low"]), "Closed / Rejected / Deferred", "0"],
], [3.0, 2.0, 7.0, 2.0], size=9, align_center_cols=(1, 3))
doc.caption("Table", "Defects by priority and by status")
cm = Counter(x["module"] for x in DEFS)
doc.table(["Module", "Critical", "Major", "Minor", "Trivial", "Total"],
          [[f"{m} {MOD[m]}"] + [str(sum(1 for x in DEFS if x["module"] == m and x["severity"] == s)) for s in sev_order]
           + [str(cm.get(m, 0))] for m in MOD]
          + [["Total"] + [str(SEV[s]) for s in sev_order] + [str(len(DEFS))]],
          [6.4, 2.0, 2.0, 2.0, 2.0, 2.0], size=9, align_center_cols=(1, 2, 3, 4, 5))
doc.caption("Table", "Defects by module and severity")
doc.image(HERE / "charts/defects_by_module.png", 15.5, "Defects by module")
doc.image(HERE / "charts/severity_priority.png", 15.5, "Defects by severity and by priority")
doc.h("5.1 Top five most critical defects", 2)
top = ["DEF-06", "DEF-02", "DEF-23", "DEF-24", "DEF-11"]
dmap = {x["id"]: x for x in DEFS}
doc.table(["ID", "Title", "Severity / priority", "Impact"],
          [[i, dmap[i]["title"], f"{dmap[i]['severity']} / {dmap[i]['priority']}", dmap[i]["impact"]] for i in top],
          [1.6, 6.0, 2.6, 6.8], size=9)
doc.caption("Table", "Top five most critical defects")
doc.p("Close behind these are DEF-22 (past days re-judged against a new goal), DEF-21 (stale progress ring), DEF-26 "
      "(camera cannot be closed) and DEF-27 (photo estimates cannot be corrected before saving). The full defect log "
      "and one report per defect are in Appendix D.")

# ================================================ 6. observations & recommendations
doc.h("6. Observations and Recommendations", 1)
doc.h("6.1 Overall functional quality", 2)
doc.p("Calori's calculation core is sound: every target and macro split we checked against the formula matched to "
      "the kilocalorie, and the safety corrections say plainly what changed and why. Offline food search is a "
      "strength – fast, regional-name aware, and clear when nothing matches. The weaknesses cluster in three places:")
doc.bullets([
    "**Edges of the safety flow** – the underweight alternatives dead-end (DEF-06), the under-18 stop does not "
    "survive a restart (DEF-02), system Back closes the app instead of going back (DEF-03), and the 'too fast' "
    "correction ignores the goal direction (DEF-07).",
    "**Consistency of saved data** – a unit preference rewrites the goal (DEF-23), the Goal screen miscalculates "
    "from the rate it shows (DEF-24), history is re-judged (DEF-22), displays go stale (DEF-21) and a second manual "
    "add gets stuck (DEF-11).",
    "**The photo review step** – proposed portions cannot be corrected (DEF-27), details are dropped (DEF-30) and "
    "the camera screen's own controls are hard to use (DEF-25, DEF-26, DEF-29).",
])
doc.h("6.2 Recommendations for fixes", 2)
doc.bullets([
    "**Fix first (High priority):** DEF-06, DEF-02, DEF-23, DEF-24, DEF-22, DEF-21, DEF-11, DEF-26, DEF-27. Each "
    "either harms a user, corrupts the diary or blocks a core action.",
    "**Then:** the Medium-priority defects, starting with the photo review (DEF-25, DEF-30), data quality "
    "of the INDB rows (DEF-13) and system Back handling (DEF-03).",
    "Show Recent foods for foods logged by hand as well as from photos (DEF-12).",
    "Store each day's target with the day, so goal changes apply only from today forward (DEF-22) – this also "
    "removes the stale-ring class of problem (DEF-21).",
    "The project's next commit (36ead9d) states that it fixes DEF-11 and DEF-24; both should be re-tested on that "
    "build rather than assumed fixed.",
])
doc.h("6.3 Recommendations for future testing", 2)
doc.bullets([
    f"**Regression:** re-run all {FAIL} failed cases after fixes, plus the whole M2 and M6 suites, since the goal engine is "
    "shared by onboarding and the Goal screen.",
    "**Real devices:** repeat M7 on physical phones with different status-bar and cut-out heights (DEF-26) and with "
    "the real camera rather than the emulator's virtual scene.",
    "**Usability (out of scope here):** the '+' button covering the last meal's calories and controls hidden behind "
    "the floating nav bar were noticed during exploration (Appendix E).",
    "**Accessibility:** TalkBack labels (several buttons have none), text scaling, contrast of grey text.",
    "**Performance:** search latency and memory on low-end devices with the 60 MB APK and the 21,800-food database; "
    "photo-analysis time on slow networks.",
    "**Compatibility:** Android 7 (the minimum supported) to 16, tablets and landscape.",
    "**Security:** the Worker shared secret is compiled into the APK; rate-limit and abuse testing of the Worker.",
    "**Reliability:** behaviour after process death mid-flow, low storage, and interrupted photo uploads.",
    "**Automation:** the formula oracle used here could become an automated regression suite for the goal engine.",
])

# ================================================ 7. conclusion & sign-off
doc.h("7. Conclusion and Sign-off", 1)
doc.h("7.1 Completion against exit criteria", 2)
crit_open = SEV["Critical"]
high_open = PRI["High"]
doc.table(["Exit criterion (Appendix A.6)", "Target", "Actual", "Met?"], [
    ["Planned test cases executed", "100%", f"{EXECUTED / N * 100:.0f}% ({EXECUTED}/{N})", "Yes"],
    ["Every failure logged as a defect with evidence", "100%", f"{FAIL} failures → {len(DEFS)} defects, all with screenshots", "Yes"],
    ["Requirements covered by at least one test", "100%", f"{len(REQS)}/{len(REQS)}", "Yes"],
    ["Pass rate", "≥ 90%", f"{PASS_PCT:.1f}%", "No"],
    ["Open Critical defects", "0", str(crit_open), "No"],
    ["Open High-priority defects", "0", str(high_open), "No"],
], [6.6, 2.4, 5.6, 2.4], size=9)
doc.caption("Table", "Exit criteria")
doc.p("The test cycle is complete: every planned case was run, every requirement was covered and every failure is "
      "documented. The quality criteria for release are not met.")
doc.h("7.2 Release recommendation", 2)
doc.p("**Not ready for release.** Release should be reconsidered when the Critical defect and all High-priority "
      "defects are fixed and verified, and the failed test cases pass on a regression run.")
doc.h("7.3 Sign-off", 2)
doc.table(["Name", "Roll no.", "Role", "Signature", "Date"], [
    ["Usman Ghani", "24f3000", "Test lead", "", REPORT_DATE],
    ["Faizan Ali", "24f3029", "Test engineer", "", REPORT_DATE],
], [3.4, 2.4, 3.0, 4.6, 3.6], size=10, zebra=False)
doc.caption("Table", "Sign-off")

# ================================================= Appendix A test plan
doc.page_break()
doc.h("Appendix A – Test Plan", 1)
doc.h("A.1 Objectives", 2)
doc.bullets(["Verify that every Calori feature behaves as its requirement states.",
             "Exercise valid, invalid, empty and boundary inputs, error handling, business rules, data handling and "
             "navigation.",
             "Log every deviation as a reproducible defect with evidence, and judge fitness for release."])
doc.h("A.2 Scope", 2)
doc.table(["In scope", "Out of scope"], [[
    ["Onboarding and all UC-02 safety rules", "Goal calculation and macro split", "Manual logging and food search",
     "Day view, entry editing, delete and undo", "Calendar", "Goal management, overrides and units, Sources screen",
     "Photo logging through the configured Worker, incl. offline and no-food cases", "Navigation incl. Android Back"],
    ["All non-functional testing: performance, security, usability, compatibility, accessibility",
     "Unit tests and automated test scripts", "iOS and other platforms",
     "Worker / model internals and prompt quality (only the app's behaviour with the answers is tested)",
     "Food-database build tools (tools/build_foods_db)", "Accuracy of the bundled nutrition data as a whole "
     "(clearly implausible rows met during testing are still reported)"],
]], [8.5, 8.5], size=9, zebra=False)
doc.caption("Table", "Scope")
doc.h("A.3 Features and modules to be tested", 2)
doc.p(f"See Table 5 (Section 2.4) – eight modules, {len(REQS)} requirements, {N} test cases.")
doc.h("A.4 Test environment", 2)
doc.p("See Table 4 (Section 2.3). One emulator was used throughout; app data was cleared between onboarding scenarios.")
doc.h("A.5 Entry criteria", 2)
doc.table(["Criterion", "Status on 11-Oct-2026"], [
    ["Release APK of commit 35e2473 builds and installs", "Met – built 20:12, installed 20:13"],
    ["Requirements baselined (FR-001 – FR-046)", "Met"],
    ["Test cases designed and reviewed, expected values computed", f"Met – {N - 1} cases before execution"],
    ["Test environment ready (emulator, density 420, photo Worker healthy)", "Met – Worker /health returned ok"],
    ["Test data ready (profiles, food images)", "Met – seven images pushed to the emulator gallery"],
], [10.0, 7.0], size=9)
doc.caption("Table", "Entry criteria")
doc.h("A.6 Exit criteria", 2)
doc.bullets(["100% of planned test cases executed.", "Every failure logged as a defect with evidence.",
             "Every requirement covered by at least one executed test case.",
             "For a release recommendation: pass rate of at least 90%, no open Critical defects and no open "
             "High-priority defects."])
doc.h("A.7 Suspension and resumption", 2)
doc.p("Testing of a module is suspended if the build cannot be installed or a defect blocks every remaining case in "
      "it; the photo module would be suspended if the Worker were down or the agreed limit of 20 paid calls were "
      "reached. Blocked cases are marked 'Blocked' with the reason. None of these occurred.")
doc.h("A.8 Roles and responsibilities", 2)
doc.p("See Table 9 (Section 3.4).")
doc.h("A.9 Task allocation", 2)
doc.table(["#", "Task", "Owner", "Start date", "End date"], [
    ["1", "Test planning, scope, entry/exit criteria", "Usman Ghani", "11-Oct-2026", "11-Oct-2026"],
    ["2", "Requirement analysis and RTM", "Faizan Ali", "11-Oct-2026", "11-Oct-2026"],
    ["3", f"Test design – M1, M2, M7 ({sum(1 for t in TCS if OWNER[t['module']] == 'Usman Ghani')} cases)", "Usman Ghani", "11-Oct-2026", "11-Oct-2026"],
    ["4", f"Test design – M3, M4, M5, M6, M8 ({sum(1 for t in TCS if OWNER[t['module']] == 'Faizan Ali')} cases)", "Faizan Ali", "11-Oct-2026", "11-Oct-2026"],
    ["5", "Environment set-up: APK build, emulator, test images", "Usman Ghani", "11-Oct-2026", "11-Oct-2026"],
    ["6", "Execution – M1, M2, M7", "Usman Ghani", "11-Oct-2026", "11-Oct-2026"],
    ["7", "Execution – M3, M4, M5, M6, M8", "Faizan Ali", "11-Oct-2026", "11-Oct-2026"],
    ["8", "Exploratory sessions EXP-01 – EXP-06", "Both", "11-Oct-2026", "11-Oct-2026"],
    ["9", "Defect logging, evidence and highlight boxes", "Faizan Ali", "11-Oct-2026", "11-Oct-2026"],
    ["10", "Test summary report, metrics and charts", "Usman Ghani", "11-Oct-2026", "11-Oct-2026"],
    ["11", "Report review and viva preparation", "Both", "12-Oct-2026", "12-Oct-2026"],
], [0.8, 8.2, 2.8, 2.6, 2.6], size=9)
doc.caption("Table", "Task allocation")
doc.h("A.10 Risks and mitigations", 2)
doc.table(["Risk", "Mitigation"], [
    ["Photo analysis costs money per call", f"Agreed limit of 20 calls; gallery images chosen to cover several cases each; {PAID} used"],
    ["Emulator differs from a real phone (camera, status bar)", "Camera cases use the gallery path; device-specific findings flagged for real-device re-test"],
    ["Earlier answers leaking between scenarios", "App data cleared before every onboarding scenario"],
    ["Expected values copied from the app's own output", "Expected values computed independently by the oracle before execution"],
    ["Deadline 12-Oct-2026", "All execution completed on 11-Oct-2026"],
], [7.0, 10.0], size=9)
doc.caption("Table", "Risks and mitigations")
doc.h("A.11 Test data", 2)
doc.p("Profiles: the reference profile (male, 30, 178 cm, 78 kg) and the boundary/decision-table profiles listed in "
      "each test case. Photo test data: the following openly licensed images from Wikimedia Commons, pushed to the "
      "emulator's gallery.")
doc.table(["File", "Commons title", "Licence", "Author"],
          [[s["file"], s["title"].replace("File:", ""), s["licence"], s["author"][:40]] for s in SOURCES],
          [3.2, 7.6, 2.6, 3.6], size=8)
doc.caption("Table", "Photo test data and licences")

# ================================================= Appendix B RTM (landscape)
sec = doc.new_section(landscape=True)
doc.h("Appendix B – Requirements and Traceability Matrix", 1)
doc.p("Each requirement is traced to the test cases that verify it, their combined result and any defects found.")
rtm = []
for rid, m, text, source, pri in REQS:
    linked = [t["id"] for t in TCS if rid in t["reqs"]]
    defs = sorted({x for t in linked for x in RES[t]["defects"]})
    rtm.append([rid, m, text, source, pri, ", ".join(linked), req_status[rid], ", ".join(defs) or "—"])
doc.table(["FR", "Mod.", "Requirement", "Source", "Pri.", "Test cases", "Result", "Defects"], rtm,
          [1.5, 1.0, 10.4, 3.3, 1.5, 3.3, 1.5, 4.0], size=8, status_col=6)
doc.caption("Table", "Requirement traceability matrix")

# ================================================= Appendix C test cases
doc.h("Appendix C – Test Cases", 1)
doc.h("C.1 Test case summary", 2)
doc.table(["ID", "Module", "Req.", "Title", "Technique", "Type", "Pri.", "Sev.", "Tester", "Status", "Defects"],
          [[t["id"], t["module"], ", ".join(t["reqs"]), t["title"], t["technique"], t["kind"], t["priority"],
            t["severity"], tester(t).split()[0], status(t["id"]), ", ".join(RES[t["id"]]["defects"]) or "—"] for t in TCS],
          [1.5, 1.4, 2.3, 7.0, 2.6, 1.7, 1.4, 1.6, 1.6, 1.4, 2.0], size=7.5, status_col=9)
doc.caption("Table", "Test case summary")
sec = doc.new_section(landscape=False)
doc.h("C.2 Detailed test cases", 2)
doc.p("Every case lists the fields the assignment requires. All cases were executed on 11 October 2026.")
for t in TCS:
    r = RES[t["id"]]
    doc.kv_table([
        ("Test Case ID", t["id"]),
        ("Module / Feature", f"{t['module']} {MOD[t['module']]}"),
        ("Linked requirement(s)", ", ".join(t["reqs"])),
        ("Title / Description", t["title"]),
        ("Technique / Type", f"{t['technique']} · {t['kind']}"),
        ("Preconditions", t["pre"]),
        ("Test steps", [f"{i}. {s}" for i, s in enumerate(t["steps"], 1)]),
        ("Test data", t["data"]),
        ("Expected result", t["expected"]),
        ("Actual result", r["actual"]),
        ("Status", r["status"]),
        ("Priority / Severity", f"{t['priority']} / {t['severity']}"),
        ("Tester / Execution date", f"{tester(t)} · {fmt_date(r['date'])}"),
        ("Evidence", ", ".join(r["evidence"]) or "—"),
        ("Defects", ", ".join(r["defects"]) or "—"),
    ], widths_cm=(3.8, 13.2), size=8.5)

# ================================================= Appendix D defects
sec = doc.new_section(landscape=True)
doc.h("Appendix D – Defect Log and Defect Reports", 1)
doc.h("D.1 Defect log", 2)
doc.table(["ID", "Title", "Module", "Severity", "Priority", "Status", "Found by", "Reporter", "Date"],
          [[x["id"], x["title"], x["module"], x["severity"], x["priority"], x["status"], ", ".join(x["found"]),
            OWNER[x["module"]], "11-Oct-2026"] for x in DEFS],
          [1.6, 10.0, 1.3, 1.8, 1.7, 1.4, 3.2, 2.8, 2.6], size=8)
doc.caption("Table", "Defect log")
sec = doc.new_section(landscape=False)
doc.h("D.2 Defect reports", 2)
doc.p("One report per defect, with the device screenshot beside it; a red highlight was added to mark the fault. "
      "The unmarked originals and any further screenshots named under Evidence are in the evidence folder "
      f"(Appendix F). Environment for every defect: {D.ENV}.")
for x in DEFS:
    doc.h(f"{x['id']} – {x['title']}", 3)
    pairs = [
        ("Defect ID", x["id"]), ("Title", x["title"]), ("Module / Feature", f"{x['module']} {MOD[x['module']]}"),
        ("Found by", ", ".join(x["found"])),
        ("Severity / Priority", f"{x['severity']} / {x['priority']}"), ("Status", x["status"]),
        ("Steps to reproduce", [f"{i}. {s}" for i, s in enumerate(x["steps"], 1)]),
        ("Expected result", x["expected"]), ("Actual result", x["actual"]), ("Impact", x["impact"]),
        ("Evidence", ", ".join(x["evidence"])), ("Reporter / Date", f"{OWNER[x['module']]} · 11-Oct-2026"),
    ]
    if x["note"]:
        pairs.append(("Note", x["note"]))
    doc.kv_table_image(pairs, HERE / "annotated" / f"{x['id']}.jpg", 4.6, widths_cm=(2.9, 9.5), size=8,
                       caption=f"{x['id']} evidence: {x['evidence'][0]} (highlight added)")
doc.page_break()

# ================================================= Appendix E exploratory
doc.h("Appendix E – Exploratory Testing Notes", 1)
doc.p("Six time-boxed sessions were run alongside the scripted cases, each with a charter. Findings that are "
      "functional defects are logged in Appendix D; usability observations are recorded here only.")
for e in D.EXPLORATORY:
    doc.kv_table([("Session", e["id"]), ("Charter", e["charter"]), ("Tester", e["tester"]),
                  ("Time (11-Oct-2026)", e["time"]), ("Findings", e["findings"])], widths_cm=(3.8, 13.2), size=9)

# ================================================= Appendix F evidence
doc.h("Appendix F – Evidence Index", 1)
doc.p("All screenshots are full-resolution PNG files (1080 × 2424) in the 'evidence' folder submitted with this "
      "report; screen videos are in the 'videos' folder.")
doc.h("F.1 Screen videos", 2)
doc.table(["File", "Shows", "Linked to", "Length"], [
    ["V1_stuck_saving_button.mp4", "'Saving…' button stays disabled; tapping it does nothing; Home has one entry", "TC-034, DEF-11", "20 s"],
    ["V2_units_toggle_wipes_goal.mp4", "Tapping 'lb' changes the caption to 'hold your current weight' and the rate to 0.5 %", "TC-061, DEF-23", "9 s"],
], [5.2, 7.4, 2.8, 1.6], size=9)
doc.caption("Table", "Screen videos")
doc.h("F.2 Screenshot index", 2)
link = {}
for t in TCS:
    for ev in RES[t["id"]]["evidence"]:
        link.setdefault(ev, []).append(t["id"])
for x in DEFS:
    for ev in x["evidence"]:
        link.setdefault(ev, []).append(x["id"])
rows = []
for f in sorted((Q / "evidence").glob("*.png")):
    name = f.stem
    if name not in link and name[:6] not in TC_BY_ID and name.startswith("TC-"):
        continue  # evidence of a test case not retained in this report
    when = dt.datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M")
    rows.append([f.name, ", ".join(sorted(set(link.get(name, [])))) or "exploratory / working shot", when])
doc.table(["File", "Linked to", "Captured"], rows, [8.2, 6.8, 2.0], size=7.5)
doc.caption("Table", "Screenshot index")
doc.h("F.3 Key passed tests", 2)
key = [("TC-014_plan", "TC-014 reference plan"), ("TC-016_refused_55", "TC-016 BMI refusal"),
       ("TC-020_floor_plan", "TC-020 calorie floor"), ("TC-033_home_after_add", "TC-033 food added")]
key2 = [("TC-046_calendar_october", "TC-046 calendar"), ("TC-069_cat_no_food", "TC-069 no food"),
        ("TC-070_offline_message", "TC-070 offline"), ("TC-072_biryani_repeat", "TC-072 repeat meal")]
doc.images_row([(annotate.small(n), lbl) for n, lbl in key], 3.9, "Key passed tests – onboarding and logging")
doc.images_row([(annotate.small(n), lbl) for n, lbl in key2], 3.9, "Key passed tests – calendar and photo path")

# ================================================= Appendix G contribution
doc.h("Appendix G – Contribution Table", 1)
contrib = []
for who in ("Usman Ghani", "Faizan Ali"):
    mods = [m for m in MOD if OWNER[m] == who]
    ntc = sum(1 for t in TCS if t["module"] in mods)
    ndef = sum(1 for x in DEFS if x["module"] in mods)
    nexp = sum(1 for e in D.EXPLORATORY if e["tester"] == who)
    contrib.append([who, ROLL[who], ", ".join(mods), str(ntc), str(ndef), str(nexp),
                    "Plan, environment, report compilation" if who == "Usman Ghani" else "RTM, defect log, report review"])
doc.table(["Member", "Roll no.", "Modules", "TCs designed & executed", "Defects reported", "Exploratory sessions",
           "Other work"], contrib, [2.8, 1.9, 2.8, 2.2, 2.0, 2.2, 3.1], size=9, align_center_cols=(3, 4, 5))
doc.caption("Table", "Contribution by member")

# ================================================= Appendix H reflection
doc.h("Appendix H – Reflection", 1)
doc.p("Testing a real application against its own written use cases taught us more than testing a toy example "
      "could. Three lessons stand out.")
doc.p("**Expected results must come from somewhere other than the app.** Writing a small calculator from the "
      "published formula before running anything meant that a wrong target could not look right to us. That is how "
      "the Goal screen's rate problem (DEF-24) showed up as a clear 220 kcal gap rather than a number we accepted.")
doc.p("**The edges are where the defects are.** Most failures came from boundaries and transitions rather than the "
      "happy path: an underweight user taking the offered alternative, restarting after a refusal, pressing Android "
      "Back, adding the same food twice, or toggling a unit with a hand-set target. Decision tables and state "
      "transition tables made us list these paths deliberately.")
doc.p("**Evidence has to be planned.** A screenshot overwritten by the next step cost us a re-check; naming every "
      "capture after its test case, and highlighting the fault on the image, made the defect reports far easier to "
      "write and to read.")
doc.p("If we repeated the exercise we would test on a physical phone as well as the emulator, budget time for "
      "re-testing fixed builds, and automate the goal-engine checks so they could be re-run on every change.")

doc.save(OUTFILE)
(HERE / "headings.json").write_text(json.dumps(doc.headings, ensure_ascii=False), encoding="utf-8")
print("saved", OUTFILE, f"{OUTFILE.stat().st_size / 1e6:.1f} MB", "tables:", doc.tables, "figures:", doc.figures)
