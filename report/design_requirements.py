"""Functional requirements for Calori 1.0.0+1 @ 35e2473.

Derived from 04-use-cases.md (UC-01..UC-12), the README and on-screen
statements in the app. Each requirement is stated as behaviour a tester can
observe; the 'source' column records where it came from.
"""

MODULES = {
    "M1": "Onboarding – Profile Entry",
    "M2": "Goal Engine & Safety Rules",
    "M3": "Manual Food Logging",
    "M4": "Day View & Entry Editing",
    "M5": "Calendar",
    "M6": "Goal Management",
    "M7": "Photo Logging",
    "M8": "Navigation",
}

MODULE_OWNER = {
    "M1": "Usman Ghani", "M2": "Usman Ghani", "M7": "Usman Ghani",
    "M3": "Faizan Ali", "M4": "Faizan Ali", "M6": "Faizan Ali", "M5": "Faizan Ali", "M8": "Faizan Ali",
}

# (id, module, requirement, source, priority)
REQUIREMENTS = [
    ("FR-001", "M1", "On first launch with no saved profile the app opens onboarding; Home cannot be reached until a goal has been saved.", "UC-01 pre/postcondition", "High"),
    ("FR-002", "M1", "The user selects sex (Male / Female); selecting an option advances to the next step.", "UC-01 step 1", "High"),
    ("FR-003", "M1", "Age accepts whole numbers only. An age under 18 ends onboarding on a refusal screen with no path forward.", "UC-02 (age < 18)", "High"),
    ("FR-004", "M1", "Height must be 100–250 cm and weight 25–400 kg (or their imperial equivalents); out-of-range or malformed values are rejected with a clear message.", "UC-01 step 1; error-handling guideline", "High"),
    ("FR-005", "M1", "Height (cm / ft'in) and weight (kg / lb) units are chosen independently; switching a unit converts any value already typed.", "README 'Metric or imperial, separately'", "Medium"),
    ("FR-006", "M1", "The user can step back to earlier onboarding questions with answers retained; a progress indicator shows position in the flow.", "Onboarding UI", "Medium"),
    ("FR-007", "M2", "The daily target is Mifflin-St Jeor BMR × activity factor, minus (loss) or plus (gain) rate × 7700 kcal/kg ÷ 7, rounded to 10 kcal; protein 1.8 g/kg (to 5 g), fat max(25 % of energy, 0.6 g/kg), carbs the remainder.", "UC-01 step 4; README", "High"),
    ("FR-008", "M2", "A target weight below BMI 18.5 is refused inline, stating the lowest healthy weight and offering an alternative: maintenance, or for a gain goal, gaining to a healthy weight.", "UC-02 table; engine contract", "High"),
    ("FR-009", "M2", "A loss goal from a user already below BMI 18.5 is refused and maintenance is offered.", "UC-02 table", "High"),
    ("FR-010", "M2", "A rate faster than 1 % of bodyweight per week is clamped to 1 %, with an explanation and the honest achievable date.", "UC-02 table", "High"),
    ("FR-011", "M2", "A loss target below the calorie floor (1500 kcal male / 1200 kcal female) is clamped to the floor and the date extended; if maintenance is already at or below the floor, the plan is set to maintain.", "UC-02 table", "High"),
    ("FR-012", "M2", "A target within ±0.5 kg of current weight is treated as maintenance.", "Engine contract", "Medium"),
    ("FR-013", "M2", "Refusal and correction messages use the units the user chose and the correct direction (loss vs gain).", "UC-02 'plain language'; README units", "Medium"),
    ("FR-014", "M2", "The plan screen shows the daily target, macro split, any correction and the projected date; 'Start tracking' saves the profile and opens Home.", "UC-01 steps 6–7", "High"),
    ("FR-015", "M3", "Search queries the offline food database and shows ranked results, each with a source badge, default serving and kcal; the × button clears the query.", "UC-05 steps 3–5", "High"),
    ("FR-016", "M3", "Search matches regional / local names (e.g. channa → chickpea, karela → bitter gourd).", "README 'Search that speaks more than English'", "Medium"),
    ("FR-017", "M3", "A query with no matches shows a helpful 'No matches' message; special characters or search operators never cause an error.", "UC-05; error handling", "Medium"),
    ("FR-018", "M3", "Before anything is typed, search shows recent and frequent foods; tapping one searches for it.", "UC-05 step 2", "Medium"),
    ("FR-019", "M3", "The portion picker offers serving units first, a quantity of 0.5–20 in 0.5 steps, and shows grams, kcal and macros scaled from per-100 g values.", "UC-05 steps 7–8", "High"),
    ("FR-020", "M3", "'Add to log' saves the food (source = database) to the day selected on Home with a meal type defaulted from the time of day, confirms it, returns to Home, and further foods can then be added.", "UC-05 step 9", "High"),
    ("FR-021", "M4", "Home shows the selected day's calories consumed against target (ring % and 'X / Y kcal'), protein against target, carbs and fat, and the day's entries.", "UC-07", "High"),
    ("FR-022", "M4", "Being over target is shown neutrally ('over today'); no negative numbers.", "UC-07 'Over target renders neutrally'", "Medium"),
    ("FR-023", "M4", "The date strip shows the last 12 days ending today (no future days) and switches the day shown.", "Home UI; UC-05 retroactive logging", "Medium"),
    ("FR-024", "M4", "Tapping an entry opens an editor to change its meal type, rescale item portions and remove items; totals update immediately.", "UC-09", "High"),
    ("FR-025", "M4", "Swiping an entry deletes it with an Undo that restores it; 'Remove this meal' deletes it.", "UC-09", "High"),
    ("FR-026", "M4", "Home figures update immediately when the goal changes.", "UC-07 / UC-10", "High"),
    ("FR-027", "M5", "The calendar shows the visible month: logged days as progress rings, unlogged past days as a neutral dot, future days dimmed and not selectable.", "UC-08 steps 1–3", "High"),
    ("FR-028", "M5", "The user can page to previous months; forward paging stops at the current month.", "UC-08 step 5", "Medium"),
    ("FR-029", "M5", "Tapping a day shows its detail (consumed vs target, macros, entries); tapping it again closes the detail.", "UC-08 step 4", "Medium"),
    ("FR-030", "M5", "The month summary shows average kcal per logged day and the number of logged days.", "Calendar UI", "Medium"),
    ("FR-031", "M5", "Past days keep the target that was in force when they were logged; goal changes apply from today forward.", "UC-10; Goal screen text", "High"),
    ("FR-032", "M6", "The Goal screen shows the saved target, macros and a caption, and lets the user change current weight, goal weight and rate (0.1–1.0 % per week) with live recalculation and automatic saving.", "UC-10", "High"),
    ("FR-033", "M6", "The recalculated target honours the rate chosen on the rate stepper.", "UC-10", "High"),
    ("FR-034", "M6", "Safety rules reapply on the Goal screen, including refusals; a refused goal is not saved.", "UC-10", "High"),
    ("FR-035", "M6", "Calories and protein can be set by hand; the engine's suggestion and a Reset stay visible; a value below the floor shows an advisory; unusable values are rejected with feedback; the macro split stays consistent with the calorie target.", "README 'A daily target you can overrule'", "Medium"),
    ("FR-036", "M6", "Weight and height units can each be changed on the Goal screen without altering the goal itself.", "Goal screen 'About' rows", "Medium"),
    ("FR-037", "M6", "'Where the food data comes from' opens the Sources screen listing each data source with its attribution.", "README data sources", "Low"),
    ("FR-038", "M7", "The camera button opens a viewfinder with a shutter, a Gallery button and an optional 'Add details' field that never takes focus automatically.", "UC-03 / UC-04 constraint", "High"),
    ("FR-039", "M7", "A meal photo is analysed into proposed items (kcal, grams, macros); nothing is logged until Save; Save logs the meal (source = AI) with its photo.", "UC-03", "High"),
    ("FR-040", "M7", "Details typed before capture are sent with the photo and applied to the portions.", "UC-04", "Medium"),
    ("FR-041", "M7", "Before saving, the user can correct proposed items: adjust the portion, edit name or macros, remove an item, and add an item the photo missed.", "UC-06", "High"),
    ("FR-042", "M7", "A photo with no food returns 'No food in that photo' with Try again and manual options, never an invented entry.", "README; UC-03", "Medium"),
    ("FR-043", "M7", "Analysis failures (offline, server error, timeout) show a specific message, Try again (photo retained) and 'Add by hand instead'.", "UC-11", "High"),
    ("FR-044", "M7", "A repeat meal reuses saved values so the same food gives the same numbers; accepted photo foods feed the Recent suggestions.", "UC-12; UC-05 step 2", "Medium"),
    ("FR-045", "M8", "The nav bar switches between Home and Goal with the active tab highlighted; '+' opens Add food; the calendar button opens the calendar.", "Shell UI", "High"),
    ("FR-046", "M8", "The Android system Back button navigates back within the app (previous onboarding step, or Home from a secondary screen) instead of leaving it.", "Android navigation convention", "Medium"),
]
