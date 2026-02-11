from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

@dataclass
class LineItem:
    sku: str
    category: str
    unit_price: float
    qty: int
    fragile: bool = False

@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    country: str
    membership: str
    coupon: Optional[str]
    items: List[LineItem]

class InvoiceService:
    def __init__(self) -> None:
        self._coupon_rate: Dict[str, float] = {
            "WELCOME10": 0.10,
            "VIP20": 0.20,
            "STUDENT5": 0.05
        }
        self._tax_rates = {"TH": 0.07, "JP": 0.10, "US": 0.08}
        self._default_tax = 0.05

    def _validate(self, inv: Invoice) -> List[str]:
        problems = []
        for item in inv.items:
            if item.qty <= 0:
                problems.append(f"Invalid quantity for {item.sku}: {item.qty}")
        return problems

    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
        problems = self._validate(inv)
        if problems:
            raise ValueError("; ".join(problems))

        subtotal, fragile_fee = self._calculate_base_costs(inv.items)

        discount, warnings = self._calculate_discount(inv, subtotal)
        shipping = self._calculate_shipping(inv.country, subtotal)
        tax = (subtotal - discount) * self._tax_rates.get(inv.country, self._default_tax)

        total = max(0, subtotal + shipping + fragile_fee + tax - discount)

        if subtotal > 10000 and inv.membership not in ("gold", "platinum"):
            warnings.append("Consider membership upgrade")

        return total, warnings

    def _calculate_base_costs(self, items: List[LineItem]) -> Tuple[float, float]:
        subtotal = sum(it.unit_price * it.qty for it in items)
        fragile_fee = sum(5.0 * it.qty for it in items if it.fragile)
        return subtotal, fragile_fee

    def _calculate_shipping(self, country: str, subtotal: float) -> float:
        if country == "TH":
            return 60 if subtotal < 500 else 0
        if country == "JP":
            return 600 if subtotal < 4000 else 0
        if country == "US":
            if subtotal < 100: return 15
            if subtotal < 300: return 8
            return 0
        return 25 if subtotal < 200 else 0

    def _calculate_discount(self, inv: Invoice, subtotal: float) -> Tuple[float, List[str]]:
        discount = 0.0
        warnings = []
        

        if inv.membership == "gold":
            discount += subtotal * 0.03
        elif inv.membership == "platinum":
            discount += subtotal * 0.05
        elif subtotal > 3000:
            discount += 20


        if inv.coupon and inv.coupon.strip():
            code = inv.coupon.strip()
            rate = self._coupon_rate.get(code)
            if rate is not None:
                discount += subtotal * rate
            else:
                warnings.append("Unknown coupon")
                
        return discount, warnings
