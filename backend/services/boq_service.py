import re

import pdfplumber


def _to_float(value: str) -> float:
    try:
        return float(str(value).replace(",", "").strip())
    except Exception:
        return 0.0


def extract_boq_items(file_path: str) -> list[dict]:
    boq_items: list[dict] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                for row in table[1:]:
                    if not row or len(row) < 5:
                        continue
                    item_name = (row[0] or "").strip()
                    quantity = _to_float(row[1])
                    unit = (row[2] or "nos").strip() or "nos"
                    unit_rate = _to_float(row[3])
                    total_cost = _to_float(row[4]) or quantity * unit_rate
                    if item_name and re.search(r"[A-Za-z]", item_name):
                        boq_items.append(
                            {
                                "item_name": item_name,
                                "quantity": quantity,
                                "unit": unit,
                                "unit_rate": unit_rate,
                                "total_cost": total_cost,
                            }
                        )
    return boq_items


def boq_analytics(boq_items: list[dict]) -> dict:
    total_cost = sum(item["total_cost"] for item in boq_items)
    total_quantity = sum(item["quantity"] for item in boq_items)
    return {
        "estimated_project_cost": round(total_cost, 2),
        "material_totals": round(total_quantity, 2),
    }
