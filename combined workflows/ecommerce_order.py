from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class OrderState(TypedDict, total=False):

    order_id: str
    customer_id: str
    product_name: str
    quantity: int
    unit_price: float

    shipping_distance: float
    discount_percentage: float
    tax_percentage: float

    payment_amount: float
    payment_attempts: int
    max_payment_attempts: int

    order_valid: bool
    order_message: str

    customer_verified: bool
    customer_message: str

    product_cost: float
    shipping_cost: float
    discount_amount: float
    tax_amount: float

    subtotal: float
    final_amount: float

    payment_valid: bool
    payment_message: str
    order_status: str
    final_confirmation: str

def validate_order(state: OrderState):

    if state["quantity"] <= 0:
        return {
            "order_valid": False,
            "order_message": "Quantity must be greater than 0."
        }

    if state["unit_price"] <= 0:
        return {
            "order_valid": False,
            "order_message": "Unit price must be greater than 0."
        }

    if state["shipping_distance"] < 0:
        return {
            "order_valid": False,
            "order_message": "Shipping distance cannot be negative."
        }

    print("Order validation successful.")

    return {
        "order_valid": True,
        "order_message": "Order is valid."
    }
## Verify customer
def verify_customer(state: OrderState):

    valid_customers = [
        "CUST001",
        "CUST002",
        "CUST003"
    ]

    if state["customer_id"] in valid_customers:

        print("Customer verified.")

        return {
            "customer_verified": True,
            "customer_message": "Customer verified successfully."
        }

    return {
        "customer_verified": False,
        "customer_message": "Customer verification failed."
    }

## calculate product cost
def calculate_product_cost(state: OrderState):

    cost = (
        state["quantity"]
        * state["unit_price"]
    )

    return {
        "product_cost": round(cost, 2)
    }
## calculate shipping cost
def calculate_shipping_cost(state: OrderState):

    distance = state["shipping_distance"]

    # Example:
    # ₹10 per km
    shipping = distance * 10

    return {
        "shipping_cost": round(shipping, 2)
    }

## calculate discount
def calculate_discount(state: OrderState):
    product_cost = state["product_cost"]

    discount = (
        product_cost
        * state["discount_percentage"]
        / 100
    )

    return {
        "discount_amount": round(discount, 2)
    }

## calculate tax
def calculate_tax(state: OrderState):

    product_cost = state["product_cost"]
    discount = state["discount_amount"]

    taxable_amount = product_cost - discount

    tax = (
        taxable_amount
        * state["tax_percentage"]
        / 100
    )

    return {
        "tax_amount": round(tax, 2)
    }

## combine bills
def combine_bill(state: OrderState):
    product = state["product_cost"]
    shipping = state["shipping_cost"]
    discount = state["discount_amount"]
    tax = state["tax_amount"]

    subtotal = product + shipping

    final_amount = (
        subtotal
        - discount
        + tax
    )

    print(f"Product cost : ₹{product}")
    print(f"Shipping     : ₹{shipping}")
    print(f"Discount     : ₹{discount}")
    print(f"Tax          : ₹{tax}")
    print(f"Final amount : ₹{final_amount}")

    return {
        "subtotal": round(subtotal, 2),
        "final_amount": round(final_amount, 2)
    }

## validate payment
def validate_payment(state: OrderState):

    payment = state["payment_amount"]
    final_amount = state["final_amount"]

    if payment == final_amount:

        print("Payment amount is valid.")

        return {
            "payment_valid": True,
            "payment_message": "Payment amount is correct."
        }

    print("Payment amount is incorrect.")

    return {
        "payment_valid": False,
        "payment_message": (
            f"Expected ₹{final_amount}, "
            f"but received ₹{payment}."
        )
    }


## process order
def process_order(state: OrderState):

    print("\n========== process_order ==========")

    return {
        "order_status": "Processed"
    }


## request_payment_correction
def request_payment_correction(state: OrderState):

    attempts = state.get("payment_attempts", 0) + 1

    print(f"Payment attempt: {attempts}")

    return {
        "payment_attempts": attempts,
        "payment_message": (
            f"Payment correction required. "
            f"Attempt {attempts}."
        )
    }

## retry_payment
def retry_payment(state: OrderState):
    attempts = state.get("payment_attempts", 0)
    print(f"Retrying payment... Attempt {attempts}")
    if attempts < 3:
        return {
            "payment_amount": state["payment_amount"]
        }
    else:
        # Simulate customer correcting the payment
        return {
            "payment_amount": state["final_amount"]
        }

## route payment
def route_payment(state: OrderState):

    if state["payment_valid"]:
        return "process_order"

    return "request_payment_correction"



def route_retry(state: OrderState):
    attempts = state.get("payment_attempts", 0)
    if attempts >= state["max_payment_attempts"]:
        return "payment_failed"
    return "retry_payment"


def check_retry_payment(state: OrderState):
    payment = state["payment_amount"]
    final_amount = state["final_amount"]

    if payment == final_amount:

        return {
            "payment_valid": True,
            "payment_message": "Payment successful."
        }

    return {
        "payment_valid": False,
        "payment_message": "Payment still incorrect."
    }


def payment_failed(state: OrderState):

    return {
        "order_status": "Payment Failed"
    }

def generate_confirmation(state: OrderState):

    if state["order_status"] == "Processed":
        confirmation = (
            f"Order {state['order_id']} confirmed successfully. "
            f"Customer: {state['customer_id']}. "
            f"Product: {state['product_name']}. "
            f"Quantity: {state['quantity']}. "
            f"Final Amount: ₹{state['final_amount']}. "
            f"Payment successful."
        )
    else:
        confirmation = (
            f"Order {state['order_id']} could not be processed. "
            f"Reason: Payment failed after "
            f"{state['payment_attempts']} attempts."
        )
    return {
        "final_confirmation": confirmation
    }

graph = StateGraph(OrderState)


## Add nodes
graph.add_node("validate_order",validate_order)
graph.add_node("verify_customer",verify_customer)
graph.add_node("calculate_product_cost",calculate_product_cost)
graph.add_node("calculate_shipping_cost",calculate_shipping_cost)
graph.add_node("calculate_discount",calculate_discount)
graph.add_node("calculate_tax",calculate_tax)
graph.add_node("combine_bill",combine_bill)
graph.add_node("validate_payment",validate_payment)
graph.add_node("process_order",process_order)
graph.add_node("request_payment_correction",request_payment_correction)
graph.add_node("retry_payment",retry_payment)
graph.add_node("check_retry_payment",check_retry_payment)
graph.add_node("payment_failed",payment_failed)
graph.add_node("generate_confirmation",generate_confirmation)

## add edges
graph.add_edge(START,"validate_order")
graph.add_edge("validate_order","verify_customer")
graph.add_edge("verify_customer","calculate_product_cost")
graph.add_edge("verify_customer","calculate_shipping_cost")
graph.add_edge("verify_customer","calculate_discount")
graph.add_edge("verify_customer","calculate_tax")
graph.add_edge("calculate_product_cost","combine_bill")
graph.add_edge("calculate_shipping_cost","combine_bill")
graph.add_edge("calculate_discount","combine_bill")
graph.add_edge("calculate_tax","combine_bill")
graph.add_edge("combine_bill","validate_payment")
graph.add_conditional_edges("validate_payment",route_payment,
    {
        "process_order": "process_order",
        "request_payment_correction":
            "request_payment_correction"
    }
)
graph.add_edge(
    "process_order",
    "generate_confirmation"
)
graph.add_conditional_edges("request_payment_correction",route_retry,
    {
        "retry_payment": "retry_payment",
        "payment_failed": "payment_failed"
    }
)
graph.add_edge("retry_payment","check_retry_payment")

def route_after_retry(state: OrderState):
    if state["payment_valid"]:
        return "process_order"
    attempts = state.get("payment_attempts", 0)
    if attempts >= state["max_payment_attempts"]:
        return "payment_failed"
    return "request_payment_correction"


graph.add_conditional_edges("check_retry_payment",route_after_retry,
    {
        "process_order": "process_order",
        "request_payment_correction":
            "request_payment_correction",
        "payment_failed": "payment_failed"
    }
)
graph.add_edge("payment_failed","generate_confirmation")
graph.add_edge("generate_confirmation",END)

## graph compile
app = graph.compile()

initial_state = {
    "order_id": "ORD1001",
    "customer_id": "CUST001",
    "product_name": "Wireless Headphones",
    "quantity": 2,
    "unit_price": 3000,
    "shipping_distance": 15,
    "discount_percentage": 10,
    "tax_percentage": 18,
    "payment_amount": 6500,
    "payment_attempts": 0,
    "max_payment_attempts": 3
}

result = app.invoke(initial_state)

print("\n\n============================================")
print("FINAL WORKFLOW RESULT")
print("============================================")

for key, value in result.items():
    print(f"{key}: {value}")