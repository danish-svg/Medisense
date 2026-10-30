"""Loads starter data the first time the database is empty."""
import random
from datetime import date, timedelta
from sqlalchemy import select
from .models import Supplier, Medicine, SalesRecord, Branch, Setting

SUPPLIERS = [("MediCore Pharma", 2, 96, 2500), ("HealthLine Distributors", 4, 88, 1500),
             ("Zenith Lifesciences", 3, 92, 3000), ("Apex Wholesale", 6, 79, 1000)]
BRANCHES = [("City Centre Branch", .85, 6), ("Airport Road Branch", .70, 14), ("Civil Lines Branch", .55, 9)]
# name, category, criticality, stock, price, expiry_days, supplier#, avg daily, shelf units, demand kind
MEDS = [
 ("Paracetamol 500mg","Analgesic","essential",420,1.2,320,1,60,1,"regular"),
 ("Amoxicillin 250mg","Antibiotic","essential",90,4.5,45,2,22,1,"surge"),
 ("Metformin 500mg","Antidiabetic","essential",260,2.1,210,1,35,1,"regular"),
 ("Atorvastatin 10mg","Cardiac","essential",130,3.8,150,3,18,1,"regular"),
 ("Cetirizine 10mg","Antihistamine","desirable",75,1,25,2,14,1,"surge"),
 ("Insulin Glargine","Antidiabetic","vital",40,480,70,3,6,2,"regular"),
 ("Omeprazole 20mg","Antacid","desirable",310,1.6,400,1,28,1,"regular"),
 ("Azithromycin 500mg","Antibiotic","essential",55,6.2,18,4,11,1,"surge"),
 ("Salbutamol Inhaler","Respiratory","vital",28,95,120,3,5,5,"surge"),
 ("ORS Sachet","Supplement","essential",500,4,9,2,40,1,"regular"),
 ("Ibuprofen 400mg","Analgesic","desirable",180,1.4,260,1,25,1,"regular"),
 ("Pantoprazole 40mg","Antacid","desirable",95,2.4,90,4,16,1,"regular"),
 ("Cough Syrup 100ml","Respiratory","desirable",60,32,35,2,9,4,"surge"),
 ("Vitamin D3 60K","Supplement","desirable",200,55,500,3,8,1,"regular"),
 ("Amlodipine 5mg","Cardiac","essential",340,1.5,380,1,30,1,"regular"),
 ("Adrenaline Injection","Cardiac","vital",12,38,150,3,0,1,"sporadic"),
 ("Anti-Snake Venom","Antidote","vital",4,650,200,3,0,2,"sporadic"),
 ("Rabies Vaccine","Vaccine","essential",9,340,40,4,0,2,"sporadic"),
]

def make_history(avg, rng, kind="regular", days=28):
    h = []
    for i in range(days):
        if kind == "sporadic":
            h.append(rng.randint(1, 3) if rng.random() < .25 else 0)
        else:
            g = 1 + i * .035 if kind == "surge" else 1
            h.append(max(1, round(avg * g * (.8 + .4 * rng.random()))))
    if kind != "sporadic" and days > 20 and rng.random() < .3:
        h[20] = round(avg * 3.4)                        # occasional bulk purchase
    return h

def history_records(h):
    """Turn a list of daily totals into dated rows ending today."""
    today = date.today()
    return [SalesRecord(sale_date=today - timedelta(days=len(h) - 1 - i), quantity=q) for i, q in enumerate(h)]

def seed(db):
    if db.scalar(select(Supplier.id).limit(1)):
        return
    rng = random.Random(11)
    sups = [Supplier(name=n, lead_time_days=lt, reliability_pct=r, min_order_value=mo) for n, lt, r, mo in SUPPLIERS]
    db.add_all(sups); db.flush()
    db.add_all([Branch(name=n, absorb_rate=a, distance_km=d) for n, a, d in BRANCHES])
    db.add_all([Setting(key="budget", value=40000), Setting(key="storage_limit", value=3700)])
    for n, c, cr, s, p, e, su, d, v, kind in MEDS:
        m = Medicine(name=n, category=c, criticality=cr, stock=s, unit_price=p, expiry_days=e,
                     storage_units=v, supplier_id=sups[su - 1].id)
        m.sales = history_records(make_history(d, rng, kind))
        db.add(m)
    db.commit()
