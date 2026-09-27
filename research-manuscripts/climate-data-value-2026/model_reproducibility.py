#!/usr/bin/env python3
"""Reproduce the paper's fictional financial illustrations. No third-party packages."""
from math import isclose

SCENARIOS = {
    "downside": dict(capex=12.0, benefit=1.6, deg=.0100, discount=.12, replace=3.2, residual=.5),
    "base": dict(capex=12.0, benefit=2.2, deg=.0050, discount=.10, replace=2.5, residual=1.0),
    "upside": dict(capex=12.0, benefit=2.8, deg=.0025, discount=.08, replace=2.0, residual=1.5),
}
EXPECTED_NPV = {"downside":-3.657, "base":1.818, "upside":8.376}
EXPECTED_IRR = {"downside":.0439, "base":.1309, "upside":.2006}

def cash_flows(s):
    return [-s["capex"]] + [
        s["benefit"]*(1-s["deg"])**(year-1)
        -(s["replace"] if year==8 else 0)
        +(s["residual"] if year==12 else 0)
        for year in range(1, 13)
    ]

def npv(flows, rate):
    return sum(cf/(1+rate)**year for year,cf in enumerate(flows))

def irr(flows):
    lo,hi=-.95,3.0
    assert npv(flows,lo)>0 and npv(flows,hi)<0
    for _ in range(120):
        mid=(lo+hi)/2
        if npv(flows,mid)>0:lo=mid
        else:hi=mid
    return (lo+hi)/2

def test():
    for name,s in SCENARIOS.items():
        cf=cash_flows(s)
        v,rate=npv(cf,s["discount"]),irr(cf)
        assert isclose(v,EXPECTED_NPV[name],abs_tol=.00055),(name,"NPV",v)
        assert isclose(rate,EXPECTED_IRR[name],abs_tol=.000055),(name,"IRR",rate)
        assert isclose(npv(cf,rate),0,abs_tol=1e-9)
        print(name, f"NPV USD {v:+.6f}m",f"IRR {rate:.5%}")
    borrower_a=40/200*150000
    borrower_b=25/100*40000
    assert borrower_a==30000 and borrower_b==10000
    closing=40000-5000-10000+7000+1000+3000
    assert closing==36000
    assert isclose((40000-closing)/40000,.10)
    flood_saved=(.10-.04)*5.0
    assert isclose(flood_saved,.30)
    annual_factor=.10/(1-(1+.10)**(-8))
    abatement=(2.0*annual_factor-.32)*1_000_000/2000
    assert 27<abatement<28
    print("PASS: scenario valuation, IRRs, loan attribution, inventory bridge, flood arithmetic, annualised abatement cost")

if __name__=="__main__":
    test()
