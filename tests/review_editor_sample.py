"""Small sample file for manually testing the NeuroCLI Review Editor."""


# This intentionally messy function gives the formatter and Review Editor
# something safe to work on without touching production code.
def calculate_total(price, quantity, discount=0):
    subtotal = price * quantity
    return subtotal - discount


# This simple print keeps the file easy to inspect after applying edits.
print(calculate_total(20, 2, 4))
