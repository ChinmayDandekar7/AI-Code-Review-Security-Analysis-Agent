"""A small, well-structured module with no known code smells."""

from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    total: float
    is_paid: bool


def calculate_discount(order: Order, percent: float) -> float:
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return order.total * (percent / 100)


def apply_discount(order: Order, percent: float) -> Order:
    discount = calculate_discount(order, percent)
    return Order(order_id=order.order_id, total=order.total - discount, is_paid=order.is_paid)


def format_receipt(order: Order) -> str:
    status = "PAID" if order.is_paid else "UNPAID"
    return f"Order {order.order_id}: ${order.total:.2f} [{status}]"
