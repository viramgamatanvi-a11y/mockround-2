"""Set C - Training Performance Analysis (Python module)
Run from the repository ROOT:   python python/analysis.py
All paths are relative to the repo root."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("outputs", exist_ok=True)

# ---------------------------------------------------------------- P1: load
assess = pd.read_csv("data/raw/assessments.csv")
courses = pd.read_csv("data/raw/courses.csv")
for col in ["score", "attendance_pct"]:
    assess[col] = pd.to_numeric(assess[col])
assess["assessment_id"] = assess["assessment_id"].astype(int)
for col in ["month", "course_id", "batch"]:
    assess[col] = assess[col].astype(str)
print("Raw rows:", len(assess), "| numeric dtypes:", assess[["score", "attendance_pct"]].dtypes.to_dict())

# ------------------------------------------------- P1: clean (drop duplicate)
before = len(assess)
assess = assess.drop_duplicates().reset_index(drop=True)
print(f"Rows before: {before} | after removing exact duplicate: {len(assess)}")

# -------------------------------------------------------- P1: merge + asserts
df = assess.merge(courses, on="course_id", how="left")
assert len(df) == 12, f"Expected 12 rows, got {len(df)}"
assert df["department"].isna().sum() == 0, "Unmatched course_id found!"
print("ASSERT OK -> merged rows = 12, NaN in department = 0")

# month is an ordered category: Jan -> Feb -> Mar
df["month"] = pd.Categorical(df["month"], categories=["Jan", "Feb", "Mar"], ordered=True)

# ------------------------------------------------------ P2: derived field
df["pass_flag"] = (df["score"] >= 50).astype(int)

# department summary (rates from underlying counts)
dept = (df.groupby("department")
          .agg(total_assessments=("pass_flag", "size"),
               passing_assessments=("pass_flag", "sum"),
               avg_score=("score", "mean"))
          .reset_index())
dept["pass_rate_pct"] = (dept["passing_assessments"] / dept["total_assessments"] * 100).round(2)
dept["avg_score"] = dept["avg_score"].round(2)
print("\nDepartment summary:\n", dept.to_string(index=False))

# course summary -> lowest pass rate
course = (df.groupby(["course_id", "course"])
            .agg(total_assessments=("pass_flag", "size"),
                 passing_assessments=("pass_flag", "sum"),
                 avg_score=("score", "mean"))
            .reset_index())
course["pass_rate_pct"] = (course["passing_assessments"] / course["total_assessments"] * 100).round(2)
course["avg_score"] = course["avg_score"].round(2)
print("\nCourse summary:\n", course.to_string(index=False))

low = course[course["pass_rate_pct"] == course["pass_rate_pct"].min()]  # report ALL ties
for _, r in low.iterrows():
    print(f"\nLOWEST PASS RATE -> {r['course']} ({r['course_id']}): "
          f"{r['passing_assessments']} passing / {r['total_assessments']} total = {r['pass_rate_pct']:.2f}%")

overall = df["pass_flag"].sum() / len(df) * 100
print(f"Overall pass rate: {df['pass_flag'].sum()}/{len(df)} = {overall:.2f}%")

# ---------------------------------------------------------- P3: chart
monthly = df.groupby("month", observed=True)["score"].mean().round(2)
print("\nMonthly average score:\n", monthly.to_string())

fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(monthly.index.astype(str), monthly.values, color="#2E75B6")
ax.bar_label(bars, fmt="%.2f", padding=3)
ax.set_title("Monthly Average Score (Jan → Feb → Mar)")
ax.set_xlabel("Month")
ax.set_ylabel("Average Score (0-100)")
ax.set_ylim(0, 100)
plt.tight_layout()
plt.savefig("outputs/python_chart.png", dpi=150)
plt.close()

# ---------------------------------------------------------- P3: exports
df_out = df.copy()
df_out["month"] = df_out["month"].astype(str)
df_out.to_csv("outputs/clean_data.csv", index=False)
dept.to_csv("outputs/python_summary.csv", index=False)
course.to_csv("outputs/python_course_summary.csv", index=False)
print("\nExported: outputs/clean_data.csv, outputs/python_summary.csv, "
      "outputs/python_course_summary.csv, outputs/python_chart.png")

# ------------------------------------- batch summary (for README / PBI check)
batch = (df.groupby("batch")
           .agg(total=("pass_flag", "size"), passing=("pass_flag", "sum"), avg_score=("score", "mean"))
           .reset_index())
batch["pass_rate_pct"] = (batch["passing"] / batch["total"] * 100).round(2)
batch["avg_score"] = batch["avg_score"].round(2)
print("\nBatch summary:\n", batch.to_string(index=False))
