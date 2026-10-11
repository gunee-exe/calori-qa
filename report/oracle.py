"""Test oracle: expected goal figures from the rules Calori publishes
(README, 01-concept.md, 04-use-cases.md UC-01/UC-02): Mifflin-St Jeor BMR x
activity factor, 7700 kcal per kg, rate capped at 1 % bodyweight/week, calorie
floor 1500 (male) / 1200 (female), BMI 18.5 lower bound, targets rounded to 10
kcal, protein 1.8 g/kg rounded to 5 g, fat max(25 % energy, 0.6 g/kg)."""
import datetime as dt, math
FACTOR = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "very": 1.725, "extra": 1.9}
TODAY = dt.date(2026, 10, 11)

def plan(sex, age, cm, kg, target, weeks=12, act="moderate", rate_pct=None):
    bmr = 10 * kg + 6.25 * cm - 5 * age + (5 if sex == "m" else -161)
    tdee = bmr * FACTOR[act]
    floor = 1500 if sex == "m" else 1200
    bmi = kg / (cm / 100) ** 2; tbmi = target / (cm / 100) ** 2
    out = {"bmr": round(bmr, 1), "tdee": round(tdee, 1), "bmi": round(bmi, 1), "target_bmi": round(tbmi, 1),
           "healthy_min_kg": round(18.5 * (cm / 100) ** 2, 1)}
    direction = "lose" if target < kg - 0.5 else "gain" if target > kg + 0.5 else "maintain"
    out["direction"] = direction
    if age < 18: return {**out, "verdict": "refused: minor"}
    if bmi < 18.5 and direction == "lose": return {**out, "verdict": "refused: already underweight"}
    if tbmi < 18.5: return {**out, "verdict": "refused: target underweight"}
    if direction == "maintain":
        return {**out, "verdict": "accepted: maintain", "kcal": round(round(tdee) / 10) * 10}
    change = abs(kg - target)
    rate = change / max(1, weeks) if rate_pct is None else kg * rate_pct / 100
    notes = []
    if rate > kg * 0.01: rate = kg * 0.01; notes.append("rate clamped")
    delta = rate * 7700 / 7
    if direction == "lose":
        if tdee <= floor:
            return {**out, "verdict": "adjusted: maintain (TDEE <= floor)", "kcal": round(round(tdee) / 10) * 10}
        if tdee - delta < floor:
            delta = tdee - floor; rate = delta * 7 / 7700; notes.append("calorie floor")
    kcal = tdee - delta if direction == "lose" else tdee + delta
    kcal = round(round(kcal) / 10) * 10
    wk = min(520, change / rate)
    date = TODAY + dt.timedelta(days=math.ceil(wk * 7))
    protein = round(1.8 * kg / 5) * 5
    fat = round(max(0.25 * kcal / 9, 0.6 * kg))
    carbs = max(0, round((kcal - protein * 4 - fat * 9) / 4))
    return {**out, "verdict": "adjusted: " + ", ".join(notes) if notes else "accepted",
            "kcal": kcal, "rate_kg_wk": round(rate, 3), "rate_pct": round(rate / kg * 100, 2),
            "weeks": round(wk, 2), "date": date.isoformat(), "protein": protein, "carbs": carbs, "fat": fat}

if __name__ == "__main__":
    cases = {
      "A reference (m30 178/78 -> 72, 12w, moderate)": ("m", 30, 178, 78, 72),
      "B too fast (m30 178/78 -> 60)": ("m", 30, 178, 78, 60),
      "C target BMI<18.5 (178/78 -> 55)": ("m", 30, 178, 78, 55),
      "D already underweight (178/55 -> 52)": ("m", 30, 178, 55, 52),
      "E underweight gain (178/52 -> 56)": ("m", 30, 178, 52, 56),
      "E2 healthy-weight alternative (178/52 -> 58.6)": ("m", 30, 178, 52, 58.6),
      "F gain too fast (178/70 -> 85)": ("m", 30, 178, 70, 85),
      "G floor (f40 155/60 -> 54 sedentary)": ("f", 40, 155, 60, 54, 12, "sedentary"),
      "H tdee<=floor (f80 150/45 -> 42 sedentary)": ("f", 80, 150, 45, 42, 12, "sedentary"),
      "I maintain edge 78.5": ("m", 30, 178, 78, 78.5),
      "I2 gain edge 78.6": ("m", 30, 178, 78, 78.6),
      "J long goal (f60 150/75 -> 45 sedentary)": ("f", 60, 150, 75, 45, 12, "sedentary"),
      "K goal screen 95->92 @1.0% (true rate)": ("m", 30, 178, 95, 92, 12, "moderate", 1.0),
      "K2 goal screen 95->92 quantised (4 weeks)": ("m", 30, 178, 95, 92, 4),
      "K0 onboarding 95->92 12w": ("m", 30, 178, 95, 92),
    }
    for name, args in cases.items():
        print(name); print("   ", plan(*args))
