# api/index.py
from fastapi import FastAPI
from pydantic import BaseModel
import bisect

app = FastAPI(title="India Salary & Invoice Calculator API")

# --- VLOOKUP TABLE ---
MARKUP_TABLE = [
    (5000, 7000), (6000, 7000), (7000, 7000), (8000, 7000), (9000, 7000),
    (10000, 7000), (11000, 7000), (12000, 7000), (13000, 7000), (13500, 7018),
    (14000, 7035), (14500, 7053), (15000, 7070), (15500, 7088), (16000, 7106),
    (16500, 7123), (17000, 7141), (17500, 7159), (18000, 7177), (18500, 7195),
    (19000, 7213), (19500, 7231), (20000, 7249), (21000, 7285), (22000, 7321),
    (23000, 7358), (24000, 7395), (25000, 7432), (26000, 7469), (27000, 7506),
    (28000, 7544), (29000, 7581), (30000, 7612), (31000, 7642), (32000, 7673),
    (33000, 7704), (34000, 7734), (35000, 7765), (36000, 7796), (37000, 7828),
    (38000, 7859), (39000, 7890), (40000, 7922), (41000, 7954), (42000, 7985),
    (43000, 8017), (44000, 8049), (45000, 8082), (46000, 8114), (47000, 8158),
    (48000, 8211), (49000, 8265), (50000, 8318), (51000, 8372), (52000, 8427),
    (53000, 8482), (54000, 8537), (55000, 8592), (56000, 8648), (57000, 8704),
    (58000, 8761), (59000, 8818), (60000, 8875), (61000, 8933), (62000, 8991),
    (63000, 9049), (64000, 9108), (65000, 9167), (66000, 9227), (67000, 9287),
    (68000, 9347), (69000, 9408), (70000, 9469), (71000, 9530), (72000, 9568),
    (73000, 9606), (74000, 9645), (75000, 9683), (76000, 9722), (77000, 9761),
    (78000, 9800), (79000, 9839), (80000, 9879), (81000, 9918), (82000, 9958),
    (83000, 9998), (84000, 10038), (85000, 10078), (86000, 10118), (87000, 10159),
    (88000, 10199), (89000, 10240), (90000, 10281), (91000, 10322), (92000, 10363),
    (93000, 10405), (94000, 10446), (95000, 10488), (96000, 10530), (97000, 10572),
    (98000, 10615), (99000, 10657), (100000, 10700), (101000, 10742), (102000, 10785),
    (103000, 10829), (104000, 10872), (105000, 10915), (106000, 10959), (107000, 11003),
    (108000, 11047), (109000, 11091), (110000, 11135), (111000, 11180), (112000, 11225),
    (113000, 11270), (114000, 11315), (115000, 11360), (116000, 11405), (117000, 11451),
    (118000, 11497), (119000, 11543), (120000, 11589)
]

MARKUP_KEYS = [row[0] for row in MARKUP_TABLE]
MARKUP_VALS = [row[1] for row in MARKUP_TABLE]

# --- INPUT MODEL ---
class SalaryInput(BaseModel):
    fixed_cost_annual: float
    bonus_annual: float
    joining_bonus: float
    exchange_rate: float

def get_markup(total_per_annum_gbp):
    if total_per_annum_gbp < MARKUP_KEYS[0]:
        return MARKUP_VALS[0]
    idx = bisect.bisect_right(MARKUP_KEYS, total_per_annum_gbp) - 1
    return MARKUP_VALS[idx]

# --- API ENDPOINT ---
@app.post("/api/calculate")
def calculate_finance(data: SalaryInput):
    # 1. Indian Salary Breakdown (Monthly)
    fixed_cost_monthly = data.fixed_cost_annual / 12
    basic_salary_monthly = fixed_cost_monthly * 0.50
    hra_monthly = basic_salary_monthly * 0.40
    commutation_allowance_monthly = 1600.00
    gratuity_monthly = basic_salary_monthly * 15 / 26 / 12

    employer_pf_monthly = 22512 / 12
    employer_medical_monthly = 1700.00

    special_allowance_monthly = fixed_cost_monthly - sum([
        hra_monthly,
        employer_medical_monthly,
        basic_salary_monthly
    ])

    total_ctc_per_annum = data.fixed_cost_annual + data.bonus_annual + data.joining_bonus

    # 2. Conversion & Markup (GBP Calculations)
    total_per_annum_gbp = total_ctc_per_annum / data.exchange_rate
    mark_up_gbp = get_markup(total_per_annum_gbp)

    total_cost_of_salary_gbp = mark_up_gbp + total_per_annum_gbp
    recruitment_fee = total_cost_of_salary_gbp * 0.10

    # 3. Monthly Invoice Breakdown (GBP)
    cost_per_month_gbp = total_cost_of_salary_gbp / 12
    office_cost_gbp = 1400 / 12
    technology_cost_gbp = 800 / 12

    total_monthly_invoice_ex_vat = cost_per_month_gbp + office_cost_gbp + technology_cost_gbp
    total_fully_loaded = total_monthly_invoice_ex_vat * 12

    # Compile Structured JSON Results
    return {
        "local_salary_inr": {
            "fixed_cost_annual": data.fixed_cost_annual,
            "basic_salary_monthly": basic_salary_monthly,
            "hra_monthly": hra_monthly,
            "special_allowance_monthly": special_allowance_monthly,
            "commutation_allowance_monthly": commutation_allowance_monthly,
            "gratuity_monthly": gratuity_monthly,
            "employer_pf_monthly": employer_pf_monthly,
            "employer_medical_monthly": employer_medical_monthly,
            "total_ctc_per_annum": total_ctc_per_annum
        },
        "invoicing_gbp": {
            "total_per_annum": total_per_annum_gbp,
            "mark_up": mark_up_gbp,
            "total_cost_of_salary": total_cost_of_salary_gbp,
            "recruitment_fee_once_off": recruitment_fee,
            "cost_per_month": cost_per_month_gbp,
            "office_cost_monthly": office_cost_gbp,
            "technology_cost_monthly": technology_cost_gbp,
            "total_monthly_invoice_ex_vat": total_monthly_invoice_ex_vat,
            "total_fully_loaded_annual": total_fully_loaded
        }
    }
