# homework4-app
# Team Rocket — E-commerce Operations Dashboard

An in-class group exercise submission for the Data App course.
Deployed with Streamlit Cloud; built following the Data App Tutorial.

- **Deployed app**: <paste your Streamlit app URL here>https://ecommerce-orders-app-8yxmt8jxzgwyojaght7pyt.streamlit.app/
- **Repository**: <paste your GitHub repo URL here>https://github.com/lsc-ivy/ecommerce-orders-app

---

## Step 1 — Dataset and Decision-Maker

**Dataset**: `ecommerce_orders_dataset.csv`
- One row = one order line (order × product).
- Time span: **2023-01-01 to 2023-12-22** (~2,000+ rows, 40 columns).
- Columns cover order time, customer profile (age, gender, country, segment, membership, CLV), product (category, subcategory, brand, unit price, quantity), transaction (discount, coupon, shipping, tax, order amount, payment), fulfilment (shipping method, warehouse region, delivery days, order status, returned, review rating), profit (margin %, profit amount), channel (device, traffic source), and season/holiday flags.
- Source: course-provided CSV (Kaggle-style e-commerce orders). **Synthetic/desensitized data** — not real transactions; used for demonstration only.
- If your instructor requires a Kaggle link, replace this line with the actual Kaggle dataset URL; the structure and code are unchanged except column names.

**Decision-maker (one role, one person)**: the **E-commerce Operations Manager**, responsible for category operations, discount policy, and returns control.

---

## Step 2 — Why a Dashboard

1. **Who looks at it, and how often?**
   The E-commerce Operations Manager, **every Monday morning** before the weekly ops meeting. During the holiday season (Nov–Dec) they check it **daily**.

2. **What decision does it support?**
   *If the Operations Manager sees return rate rising in a category, or margin compressed in the >30% discount band, they will lower that category's discount cap, flag the high-return SKUs for QC/delisting, and contact the supplier.*

3. **What do they do today without it — and what does that cost?**
   They export the CSV and build manual Excel pivots every week (about 2–3 hours). Because returns and discounts live in different tables, "high discount + high return" combinations are easy to miss, so profit erosion is only noticed after the fact.

4. **Why a dashboard rather than a weekly email, a report, or an alert?**
   The same questions recur every week and require drill-down by category and discount band. A weekly email is static and cannot be drilled into; an alert only covers a single threshold. A dashboard (plus one return-rate alert) fits the decision better.

---

## Step 3 — What We Show, What We Cut, and the Page Order

### Headline metrics (three, within 5 seconds)
Shown side by side with `st.columns` + `st.metric`:
1. **Total sales** — is the business healthy?
2. **Overall return rate** (`Returned == 'Yes'`) — experience and profit risk.
3. **Average profit margin** (`Profit_Margin_Percent` mean) — is discounting hurting margin?

### Supporting charts (why the numbers moved)
- **Chart 1 — Monthly sales and return rate** (dual-axis line/bar over time): shows trend and holiday-season peaks.
- **Chart 2 — Return rate and average profit margin by discount band** (0 / 1–10 / 11–20 / 21–30 / >30%): directly explains why return rate and margin move.

### The only filter the manager actually needs
- **Product category** (sidebar multi-select) — the manager owns categories, so a category selector is more useful than ten sliders.
- Optional: **Holiday season** toggle (Yes / No / ALL), applied via a form so the page only refreshes on "Apply".

### Two things we chose NOT to show (and why)
1. **City-level map / city ranking** — the EDA shows `Country` and `City` are inconsistent (e.g. Germany–Dubai, France–London, India–Berlin). City is not trustworthy here; showing it would mislead the viewer. Geography is therefore analyzed by **Country only**.
2. **Customer Lifetime Value (CLV) distribution** — many CLV values are exactly **50000** (a capped value). A distribution chart would suggest a large population of ultra-high-value customers, which is false, and it does not change any operational decision.

### Data issues that could mislead the viewer — and how the dashboard handles them
- **Capped values** in `Customer_Lifetime_Value` (50000) and `Profit_Margin_Percent` (3%): noted in a caption under the metrics; averages are read with this caveat.
- **`Returned == 'Yes'` with `Order_Status == 'Delivered'`** (delivered-then-returned): counted as a return; the caption states the definition.
- **December is incomplete** (data ends 2023-12-22): the last bar in the monthly chart is flagged in a caption so it is not misread as a drop.
- **`City` unreliable**: geographic analysis uses `Country` only (see above).

### Page order (top to bottom, matching importance)
1. Title + one-line caption (who it is for, what decision it supports) + data period / refresh line.
2. Three headline metrics (`st.metric`, side by side).
3. Filters (category multi-select; holiday-season form).
4. Monthly sales & return rate chart — *why* a headline number moved.
5. Discount-band chart — *why* return rate / margin moved.
6. Bottom: collapsible detail table (`st.expander` + `st.dataframe`) for anyone who wants to drill in; can be removed if unused.

Every element passed the test: *if this disappeared, would the decision-maker notice?* If not, it was cut.

---

## Step 4 — Refresh Frequency

1. **How often should the data refresh in production?**
   **Nightly batch.** Order and return data only need daily aggregation; the decisions are weekly/daily. Real-time refresh would require pulling from several systems (POS/OMS) at extra cost without changing any decision.

2. **How often should someone review it — is that the same thing?**
   Different. Data refreshes **nightly**; the manager reviews it **weekly (Monday)**; during Nov–Dec they review it **daily**.

3. **What should be tracked over time, and what should trigger action?**
   Track **overall return rate** and **margin in the >30% discount band**. Trigger: when a category's return rate rises **≥2 percentage points week-over-week**, or margin in the >30% band falls **below 10%**, the manager should investigate the same day. This is implemented as an **alert**, not as a dashboard element checked daily.

4. **What does stale data cost?**
   One day late: extra discounted stock ships and extra returns occur, directly eroding that week's profit. One week late: the window to adjust discounts is missed.

**Line shown on the dashboard**:
`Data: 2023-01-01 – 2023-12-22 (course snapshot; Dec incomplete) · Production refresh: nightly; reviewed weekly (daily in Nov–Dec)`

---

## Step 5 — Build and Deploy

**Project setup** (following the Data App Tutorial):
```bash
uv init --python 3.14 ecommerce-ops
cd ecommerce-ops
uv add streamlit pandas matplotlib
# place ecommerce_orders_dataset.csv in this folder
