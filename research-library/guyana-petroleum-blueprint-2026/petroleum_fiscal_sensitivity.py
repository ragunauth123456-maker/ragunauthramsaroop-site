#!/usr/bin/env python3
"""Synthetic PSA-mechanism model. NOT a Stabroek forecast or contract-law opinion."""
from decimal import Decimal, ROUND_HALF_UP
from itertools import product
from pathlib import Path
import csv,json

D=Decimal
BASE=Path(__file__).resolve().parent
ROYALTY=D(".02")
COST_CEILING=D(".75")
GOV_PROFIT_SPLIT=D(".50")
def one_period(volume,price,opening_bank,new_cost):
    gross=D(str(volume))*D(str(price))
    available=D(str(opening_bank))+D(str(new_cost))
    cost_oil=min(gross*COST_CEILING,available)
    royalty=gross*ROYALTY
    profit_oil=gross-cost_oil
    gov_profit=profit_oil*GOV_PROFIT_SPLIT
    contractor_profit=profit_oil-gov_profit
    return {"gross_usd":gross,"royalty_usd":royalty,
            "eligible_cost_bank_open_plus_new_usd":available,
            "recovered_cost_usd":cost_oil,
            "unrecovered_cost_bank_close_usd":available-cost_oil,
            "profit_petroleum_value_usd":profit_oil,
            "government_profit_value_usd":gov_profit,
            "contractor_profit_value_usd":contractor_profit,
            "illustrative_government_total_usd":royalty+gov_profit,
            "government_share_gross_pct":(royalty+gov_profit)/gross*100 if gross else None}
def cashout(data,scenario):
    rows=[]
    bank=D("0")
    for year,(vol,price,newcost) in enumerate(data,1):
        q=one_period(vol,price,bank,newcost)
        rows.append({"scenario":scenario,"synthetic_year":year,
                     "saleable_barrels":vol,"price_usd_per_barrel":price,
                     "new_eligible_cost_usd":newcost,
                     "opening_cost_bank_usd":bank,**q})
        bank=q["unrecovered_cost_bank_close_usd"]
    return rows
base=[(20000000,65,1200000000),(25000000,65,800000000),(28000000,65,500000000)]
paths={"base":base,
       "low_price":[(v,45,c) for v,p,c in base],
       "high_price":[(v,95,c) for v,p,c in base],
       "startup_delay":[(0,65,100000000),base[0],base[1],base[2]],
       "cost_overrun":[(v,p,int(c*1.30)) for v,p,c in base]}
rows=[]
for name,inputs in paths.items():
    rows.extend(cashout(inputs,name))
# One-month sample from operating blueprint.
example=one_period(100000,70,50000000,5000000)
assert example["illustrative_government_total_usd"]==D("1015000")
assert example["unrecovered_cost_bank_close_usd"]==D("49750000")
assert example["government_share_gross_pct"]==D("14.5000")
# A purely synthetic same-period accounting comparison; not a lifetime welfare claim.
A_gross=D("1000000000")
B_dev=D("900000000")
A_cost=D("100000000")
combined=one_period(10000000,100,0,A_cost+B_dev)
separated=one_period(10000000,100,0,A_cost)
assert combined["illustrative_government_total_usd"]==D("145000000")
assert separated["illustrative_government_total_usd"]==D("470000000")
assert separated["illustrative_government_total_usd"]-combined["illustrative_government_total_usd"]==D("325000000")
# All statements balance; no negative recovered cost or negative bank.
for row in rows:
    assert row["gross_usd"]==row["recovered_cost_usd"]+row["profit_petroleum_value_usd"]
    assert row["profit_petroleum_value_usd"]==row["government_profit_value_usd"]+row["contractor_profit_value_usd"]
    assert row["unrecovered_cost_bank_close_usd"]>=0
    assert row["recovered_cost_usd"]<=row["gross_usd"]*COST_CEILING
target=BASE/"EDITION2_SYNTHETIC_FISCAL_SCENARIOS.csv"
with target.open("w",newline="",encoding="utf-8") as f:
    fieldnames=list(rows[0].keys())
    w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader()
    for row in rows:w.writerow({k:str(v) if isinstance(v,D) else ("not_applicable" if v is None else v) for k,v in row.items()})
def rnd(x):return str(D(x).quantize(D("0.01"),rounding=ROUND_HALF_UP))
summary={"model":"transparent synthetic mechanical illustration, not government revenue forecast",
         "contract_mechanic_sources":["S02","S15"],
         "volume_price_cost_scenarios":list(paths),
         "monthly_example":{"government_total_usd":rnd(example["illustrative_government_total_usd"]),
           "ending_cost_bank_usd":rnd(example["unrecovered_cost_bank_close_usd"]),
           "gov_share_gross_pct":rnd(example["government_share_gross_pct"])},
         "cross_project_cost_allocation":{"combined_timing_example_gov_total_usd":rnd(combined["illustrative_government_total_usd"]),
            "separated_timing_example_gov_total_usd":rnd(separated["illustrative_government_total_usd"]),
            "same_period_difference_usd":rnd(separated["illustrative_government_total_usd"]-combined["illustrative_government_total_usd"]),
            "caution":"Not a discounted lifetime comparison; development cost can be recovered in future periods"},
         "rows":len(rows),"checks":"passed"}
(BASE/"EDITION2_FISCAL_MODEL_AUDIT.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
