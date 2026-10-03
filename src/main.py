import numpy as np
import matplotlib.pyplot as plt


# -----------------------------
# 1. Town settings
# -----------------------------

TOWN_SIZE = 10
NUMBER_OF_CUSTOMERS = 100

np.random.seed(42)

customers_x = np.random.uniform(0, TOWN_SIZE, NUMBER_OF_CUSTOMERS)
customers_y = np.random.uniform(0, TOWN_SIZE, NUMBER_OF_CUSTOMERS)


# -----------------------------
# 2. Restaurant settings
# -----------------------------

restaurant_a = (3, 5)
restaurant_b = (7, 5)

price_a = 150
price_b = 170

quality_a = 4
quality_b = 3

delivery_radius_a = 6
delivery_radius_b = 6


# -----------------------------
# 3. Calculate travel distance
# -----------------------------

distance_a = np.sqrt(
    (customers_x - restaurant_a[0]) ** 2
    + (customers_y - restaurant_a[1]) ** 2
)

distance_b = np.sqrt(
    (customers_x - restaurant_b[0]) ** 2
    + (customers_y - restaurant_b[1]) ** 2
)



delivery_available_a = distance_a <= delivery_radius_a
delivery_available_b = distance_b <= delivery_radius_b

delivery_fee_a = 10 + 2 * distance_a
delivery_fee_b = 10 + 2 * distance_b

delivery_cost_a = (
    price_a
    + delivery_fee_a
    - 5 * quality_a
)

delivery_cost_b = (
    price_b
    + delivery_fee_b
    - 5 * quality_b
)


# -----------------------------
# 4. Calculate effective cost
# -----------------------------

effective_cost_a = (
    price_a
    + 10 * distance_a
    - 5 * quality_a
)

effective_cost_b = (
    price_b
    + 10 * distance_b
    - 5 * quality_b
)

# -----------------------------
# 5. Customer chooses restaurant
# -----------------------------

# Start with dine-in cost
best_cost_a = effective_cost_a
best_cost_b = effective_cost_b

# Use delivery if it is available
best_cost_a = np.where(
    delivery_available_a,
    np.minimum(effective_cost_a, delivery_cost_a),
    effective_cost_a
)

best_cost_b = np.where(
    delivery_available_b,
    np.minimum(effective_cost_b, delivery_cost_b),
    effective_cost_b
)

# Customer chooses the restaurant with lower cost
customers_choose_a = best_cost_a < best_cost_b
customers_choose_b = best_cost_b <= best_cost_a


# -----------------------------
# 6. Calculate results
# -----------------------------

customers_a = np.sum(customers_choose_a)
customers_b = np.sum(customers_choose_b)

market_share_a = customers_a / NUMBER_OF_CUSTOMERS * 100
market_share_b = customers_b / NUMBER_OF_CUSTOMERS * 100


# -----------------------------
# 7. Display results
# -----------------------------

print("----- RESTAURANT RESULTS -----")

print()
print("Restaurant A")
print(f"Price: ₹{price_a}")
print(f"Quality: {quality_a}/5")
print(f"Customers: {customers_a}")
print(f"Market Share: {market_share_a:.2f}%")

print()
print("Restaurant B")
print(f"Price: ₹{price_b}")
print(f"Quality: {quality_b}/5")
print(f"Customers: {customers_b}")
print(f"Market Share: {market_share_b:.2f}%")


# -----------------------------
# 8. Plot the town
# -----------------------------

plt.figure(figsize=(8, 8))

plt.scatter(
    customers_x[customers_choose_a],
    customers_y[customers_choose_a],
    label="Customers → Restaurant A",
    alpha=0.6
)

plt.scatter(
    customers_x[customers_choose_b],
    customers_y[customers_choose_b],
    label="Customers → Restaurant B",
    alpha=0.6
)

plt.scatter(
    restaurant_a[0],
    restaurant_a[1],
    marker="s",
    s=150,
    label="Restaurant A"
)

plt.scatter(
    restaurant_b[0],
    restaurant_b[1],
    marker="s",
    s=150,
    label="Restaurant B"
)

plt.xlim(0, TOWN_SIZE)
plt.ylim(0, TOWN_SIZE)

plt.xlabel("X Location")
plt.ylabel("Y Location")

plt.title("Restaurant Location Game - Price & Quality")

plt.grid(True)
plt.legend()

plt.show()