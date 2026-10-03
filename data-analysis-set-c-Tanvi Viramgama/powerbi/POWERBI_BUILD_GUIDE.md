# Power BI Build Guide (Set C) - follow top to bottom (~25-30 min)

> `dashboard.pbix` is a binary file that can only be created inside **Power BI Desktop**.
> This guide gives every click, M step and DAX formula so you can build it fast. Save as `powerbi/dashboard.pbix`.

## 1. Load the data
1. Home > **Get data > Text/CSV** > `data/raw/assessments.csv` > **Transform Data**.
2. Repeat for `data/raw/courses.csv` > **Transform Data**.
3. Rename queries exactly: **assessments** and **courses**.

## 2. Power Query (B1 - 1 mark)
In **assessments** > Home > *Advanced Editor*, paste:

```m
let
    Source   = Csv.Document(File.Contents("C:\YOUR\PATH\data\raw\assessments.csv"),
                [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                 {"assessment_id", Int64.Type}, {"month", type text},
                 {"course_id", type text},      {"batch", type text},
                 {"score", type number},        {"attendance_pct", type number}}),
    NoDupes  = Table.Distinct(Typed),                       // 13 -> 12 rows
    MonthNo  = Table.AddColumn(NoDupes, "month_order",
                 each if [month] = "Jan" then 1 else if [month] = "Feb" then 2 else 3, Int64.Type)
in
    MonthNo
```

In **courses** > *Advanced Editor*:

```m
let
    Source   = Csv.Document(File.Contents("C:\YOUR\PATH\data\raw\courses.csv"),
                [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                 {"course_id", type text}, {"course", type text}, {"department", type text}})
in
    Typed
```
Replace `C:\YOUR\PATH\` with your real folder. Check: assessments shows **12 rows** (View > Column profile > *Based on entire data set*). Close & Apply.

## 3. Model (B1 - 1 mark)
*Model view* > drag **courses[course_id] -> assessments[course_id]**.
Edit relationship: Cardinality **One to many (1:*)**, Cross-filter direction **Single**, **Make this relationship active** ticked.

Select **assessments[month]** > Column tools > **Sort by column > month_order**.

## 4. DAX measures (B2 - 3 marks)
Home > **Enter data** > create an empty table named **Measures** (one column, load it), then add three measures *in that table* (right-click Measures > New measure):

```dax
Assessment Count = COUNTROWS(assessments)

Avg Score = AVERAGE(assessments[score])

Pass Rate =
DIVIDE(
    COUNTROWS(FILTER(assessments, assessments[score] >= 50)),
    COUNTROWS(assessments),
    0
)
```
Format **Pass Rate** as Percentage with 2 decimals, **Avg Score** as Decimal (2 places). Delete the helper column from the Measures table (hide it).

## 5. Report page (B3 - 1 mark)
| Element | How |
|---|---|
| 3 KPI cards | Card visual x3: Assessment Count, Avg Score, Pass Rate |
| Bar chart by department | Clustered bar: Axis = `courses[department]`, Values = `Avg Score` (add `Pass Rate` as a 2nd chart if you wish) |
| Monthly trend | Column or line: Axis = `assessments[month]` (sorted by month_order -> Jan, Feb, Mar), Values = `Avg Score` |
| Batch slicer | Slicer: Field = `assessments[batch]`, style *List* or *Tile* |

Add titles to every visual, axis titles on charts, and a page title "Set C - Training Performance".

## 6. Expected values (use to verify your report)
| State | Assessment Count | Avg Score | Pass Rate |
|---|---|---|---|
| **Unfiltered** | 12 | 61.50 | 66.67% |
| Batch = Morning | 4 | 61.25 | 75.00% |
| Batch = Evening | 4 | 67.00 | 75.00% |
| Batch = **Weekend** | 4 | 56.25 | 50.00% |
| Department = Technology (via bar-chart click) | 6 | 56.00 | 50.00% |
| Department = Business | 6 | 67.00 | 83.33% |

Monthly avg (unfiltered): Jan 55.00, Feb 62.75, Mar 66.75.

## 7. Slicer demo + screenshot (B3 - 1 mark)
1. Click **Weekend** -> note cards: 4 / 56.25 / 50.00%. (Take a quick note/screenshot for the video.)
2. Clear the slicer (eraser icon) -> unfiltered state.
3. Screenshot the unfiltered page -> save as `outputs/powerbi_dashboard.png` (Win+Shift+S, or File > Export > PDF then snip).
4. Save as `powerbi/dashboard.pbix`.

## 8. Refresh instructions (copy into README - already drafted there)
Home > Transform data > Data source settings > select the two CSV sources > **Change Source...** > browse to the cloned `data/raw/` files > OK > Close & Apply > Refresh.
(Alternative: Transform data > `assessments` > Advanced Editor and edit the `File.Contents("...")` path.)
