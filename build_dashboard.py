"""Build a portable, offline dashboard from the reconciled carrier-month CSV."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data/carrier_month_combined.csv"
OUTPUT = ROOT / "Airline_Reliability_Dashboard.html"
COUNTS = ("flights", "cancelled", "diverted", "arrivals_measured", "on_time_arrivals", "late_arrivals", "arrival_status_missing")


def main():
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or len({(r["month"], r["marketing_carrier"]) for r in rows}) != len(rows):
        raise ValueError("Expected unique, nonempty carrier-month rows")
    for row in rows:
        for key in COUNTS:
            row[key] = int(row[key])
        if row["flights"] != row["cancelled"] + row["diverted"] + row["arrivals_measured"] + row["arrival_status_missing"]:
            raise ValueError("Flight balance failed")
        if row["arrivals_measured"] != row["on_time_arrivals"] + row["late_arrivals"]:
            raise ValueError("Arrival balance failed")
        row.pop("on_time_rate_completed", None)
    payload = json.dumps(rows, separators=(",", ":")).replace("<", "\\u003c")
    template = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Airline Reliability | BTS 2025</title><style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#14283d;background:#f3f6fa}*{box-sizing:border-box}body{margin:0}header{background:#102b47;color:white;padding:2rem max(5vw,20px)}header h1{margin:.2rem 0;font-size:clamp(1.8rem,3vw,3rem)}header p{max-width:850px;line-height:1.5;color:#d6e5f3}main{max-width:1450px;margin:auto;padding:1.5rem}section{background:white;border:1px solid #dce5ee;border-radius:12px;padding:1.25rem;margin-bottom:1rem;box-shadow:0 3px 14px #15314e0b}h2{margin:.1rem 0 1rem;font-size:1.2rem}.filters{display:flex;gap:1rem;flex-wrap:wrap}label{display:grid;gap:.4rem;font-weight:600}select{font:inherit;padding:.55rem;min-width:170px;border:1px solid #8ba1b5;border-radius:6px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem}.card{margin:0}.value{font-size:1.8rem;font-weight:750;color:#0c5b91}.label{color:#506477;font-size:.9rem}.grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.barrow{display:grid;grid-template-columns:60px 1fr 80px;align-items:center;gap:.6rem;margin:.8rem 0}.track{height:18px;background:#e8f0f7;border-radius:4px}.fill{height:100%;background:#1786bd;border-radius:4px}.muted{color:#536779;line-height:1.5}.warning{border-left:4px solid #b66a00;padding:.7rem 1rem;background:#fff7e6}table{border-collapse:collapse;width:100%}th,td{padding:.6rem;text-align:right;border-bottom:1px solid #e1e8ef}th:first-child,td:first-child{text-align:left}th{background:#edf3f8}div.scroll{overflow-x:auto}a{color:#086294}@media(max-width:850px){.grid{grid-template-columns:1fr}}
</style><header><small>PUBLIC DATA · BOUNDED ANALYSIS</small><h1>Airline reliability, by carrier and month</h1><p>U.S. BTS marketing-carrier on-time performance · January–February 2025. Explore reported flights, cancellation and diversion counts, and arrival punctuality among measured completed arrivals.</p></header><main>
<section><div class="filters"><label>Month<select id="month"></select></label><label>Marketing carrier code<select id="carrier"></select></label></div><p class="muted">Filters recalculate every rate from summed counts. Carrier codes reflect the source extract; comparisons need coverage and operating-context review.</p></section>
<div class="cards" id="cards"></div><div class="grid"><section><h2>On-time arrivals by carrier</h2><div id="bars"></div></section><section><h2>Monthly view</h2><div class="scroll"><table><thead><tr><th>Month</th><th>Flights</th><th>Measured arrivals</th><th>On-time rate</th><th>Cancelled</th><th>Diverted</th></tr></thead><tbody id="months"></tbody></table></div></section></div>
<section><h2>Interpretation and limits</h2><p class="warning">This is a descriptive portfolio analysis. The displayed on-time rate excludes cancellations, diversions, and missing arrival status from its denominator. It is not a claim about causes, service improvements, or exact agreement with every published BTS metric.</p><p class="muted">The downloaded source months reconcile to 1,158,590 flight rows across 20 carrier-month records. The report is a static local snapshot, not a live feed. Raw source files and transformation scripts are documented in the project README.</p><p><a href="https://catalog.data.gov/dataset/u-s-marketing-air-carriers-on-time-performance">BTS dataset description</a></p></section></main>
<script id="records" type="application/json">__PAYLOAD__</script><script>
const rows=JSON.parse(document.getElementById('records').textContent), month=document.getElementById('month'),carrier=document.getElementById('carrier');
function options(el,vals){el.innerHTML='<option value="all">All</option>'+vals.map(v=>`<option value="${v}">${v}</option>`).join('')}
options(month,[...new Set(rows.map(r=>r.month))].sort());options(carrier,[...new Set(rows.map(r=>r.marketing_carrier))].sort());
const fmt=n=>n.toLocaleString('en-US'),pct=(a,b)=>b?`${(100*a/b).toFixed(2)}%`:'—';
function sum(list,key){return list.reduce((n,r)=>n+r[key],0)}
function render(){let filtered=rows.filter(r=>(month.value==='all'||r.month===month.value)&&(carrier.value==='all'||r.marketing_carrier===carrier.value));
const metrics=[['Flights',fmt(sum(filtered,'flights'))],['Measured arrivals',fmt(sum(filtered,'arrivals_measured'))],['On-time among measured arrivals',pct(sum(filtered,'on_time_arrivals'),sum(filtered,'arrivals_measured'))],['Cancelled',fmt(sum(filtered,'cancelled'))],['Diverted',fmt(sum(filtered,'diverted'))],['Missing arrival status',fmt(sum(filtered,'arrival_status_missing'))]];
document.getElementById('cards').innerHTML=metrics.map(([k,v])=>`<section class="card"><div class="label">${k}</div><div class="value">${v}</div></section>`).join('');
let groups=[...new Set(filtered.map(r=>r.marketing_carrier))].map(code=>({code,measured:sum(filtered.filter(r=>r.marketing_carrier===code),'arrivals_measured'),on:sum(filtered.filter(r=>r.marketing_carrier===code),'on_time_arrivals')})).sort((a,b)=>b.on/b.measured-a.on/a.measured);
document.getElementById('bars').innerHTML=groups.map(g=>`<div class="barrow"><b>${g.code}</b><div class="track"><div class="fill" style="width:${100*g.on/g.measured}%"></div></div><span>${pct(g.on,g.measured)}</span></div>`).join('')||'<p>No records</p>';
let monthly=[...new Set(filtered.map(r=>r.month))].sort();document.getElementById('months').innerHTML=monthly.map(m=>{let a=filtered.filter(r=>r.month===m);return `<tr><td>${m}</td><td>${fmt(sum(a,'flights'))}</td><td>${fmt(sum(a,'arrivals_measured'))}</td><td>${pct(sum(a,'on_time_arrivals'),sum(a,'arrivals_measured'))}</td><td>${fmt(sum(a,'cancelled'))}</td><td>${fmt(sum(a,'diverted'))}</td></tr>`}).join('')}
month.addEventListener('change',render);carrier.addEventListener('change',render);render();</script></html>"""
    OUTPUT.write_text(template.replace("__PAYLOAD__", payload), encoding="utf-8")
    print(f"Wrote {OUTPUT.name}: {len(rows)} checked carrier-month rows")


if __name__ == "__main__":
    main()
