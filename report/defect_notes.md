# Running defect notes (confirmed on device)
DEF-01 Out-of-range onboarding inputs disable Continue with no message (age 0/120/999/blank; height 99/251; weight ...) - TC-005, TC-007, TC-008?
DEF-02 Under-18 refusal not persisted: force-stop + relaunch restarts onboarding, age 25 accepted - TC-013
DEF-03 System Back during onboarding closes app; reopening loses all answers (restarts at step 1) - TC-012
DEF-04 Inches field accepts 12-99 (5 ft 25 in accepted) - TC-009
DEF-05 Progress bar shows 100% on activity step (step 5 of 6) - seen during TC-014 (EXP)
OBS: target weight field does not take focus automatically (keyboard must be opened by tapping)
OBS: deleting digits passes through refused values, keyboard auto-closes after 0.9 s (usability, out of scope)
DEF-06 CRITICAL: underweight user's alternatives ('Aim for a healthy weight instead' AND 'Maintain instead') -> plan screen endless spinner, no way out - TC-018, TC-077 (new)
DEF-07 Rate-too-fast message says 'losing' for a gain goal - TC-019
DEF-08 Refusal message quotes kg when lb chosen - TC-023
DEF-09 Projected date has no year (7 Feb 2029 shown as '7 February') - TC-024
DEF-10 Raw portion code '90000' shown as default serving label (USDA Rice cake, Rice paper) - TC-026 (found)
DEF-11 'Add to log' stuck on 'Saving...' after first manual add - TC-034 (video V2)
DEF-12 'Recent' suggestions never shown for manually logged foods (UC-05 step 2) - TC-030
DEF-13 Implausible nutrition row: 'Spinach chickpeas cutlet' INDB 1 cutlet = 328 g / 2,255 kcal / 241 g fat - EXP (found in TC-027 scroll)
DEF-14 Multiplier chip labelled '0.8x' applies 0.75x (151 g -> 113 g) - EXP during TC-040
DEF-15 Repeated 0.5x shrinks item to 0 g / 0 kcal; 0-kcal meal stays in list - TC-041
DEF-16 Undo re-inserts deleted entry with new time -> moves position - TC-043
OBS: '+' FAB covers last meal card's kcal figure (layout)
OBS: INDB 'Boiled egg (Ubla anda)' 1 egg = 151 g but 68 kcal (45 kcal/100g) - add to DEF-13 examples
DEF-17 Calendar day detail omits fat - TC-049
DEF-18 Day detail survives month change; shows '0 kcal' with entries listed - TC-050
DEF-19 Hand-set kcal 0/blank silently discarded, no feedback - TC-059
DEF-20 Hand-set protein over the calorie budget accepted; macros exceed kcal - TC-060
DEF-21 Home ring % (and calendar) stale after goal change; line updates - TC-045
DEF-22 Past days re-judged against new target (Home + calendar) - TC-052
DEF-23 Weight-unit toggle on Goal erases target date + hand-set override flag (caption 'hold current weight', rate 0.5 %) - TC-061 (video V3)
DEF-24 Goal screen ignores chosen rate (1.0 % -> 'At 0.8 %', 2,150 vs 1,930 kcal) - TC-056 (also TC-055 at 78->70)
DEF-25 Viewfinder Gallery button label invisible: pill fills the bar, 'Gallery' text hidden under shutter - TC-063
DEF-26 Viewfinder Close (x) under status bar, untappable except 5 px sliver - TC-063
DEF-27 Proposed item portion cannot be adjusted (control only for low-confidence items) - TC-066
DEF-28 Proposed item name/macros not editable (UC-06 variations missing) - TC-067
DEF-29 After saving a gallery photo the app returns to the viewfinder, not Home - TC-064
DEF-30 Details hint ignored for gallery photos - TC-065
DEF-31 'Add something it missed' saves a separate entry immediately instead of appending to the photo meal - TC-068
DEF-32 Search field and results out of sync (Recent chip, pushed Add food): results under empty box, no x - TC-073, TC-071
paid calls used: 6
