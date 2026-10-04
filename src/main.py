import numpy as np
import matplotlib.pyplot as plt

TOWN_SIZE = 10
NUMBER_OF_CUSTOMERS = 100

np.random.seed(42)

# Simulated demand clusters: (name, centre_x, centre_y, spread, customers)
ANCHORS = [
    ("Town centre",       5.0, 5.0, 1.0, 40),
    ("Shopping mall",     2.0, 8.0, 0.8, 20),
    ("Business district", 8.0, 2.5, 0.8, 20),
]
NUMBER_UNIFORM = NUMBER_OF_CUSTOMERS - sum(a[4] for a in ANCHORS)

xs, ys = [], []
for _, cx, cy, spread, n in ANCHORS:
    xs.append(np.random.normal(cx, spread, n))
    ys.append(np.random.normal(cy, spread, n))
xs.append(np.random.uniform(0, TOWN_SIZE, NUMBER_UNIFORM))
ys.append(np.random.uniform(0, TOWN_SIZE, NUMBER_UNIFORM))

customers_x = np.clip(np.concatenate(xs), 0, TOWN_SIZE)
customers_y = np.clip(np.concatenate(ys), 0, TOWN_SIZE)

restaurant_a = (3, 5)
restaurant_b = (7, 5)
price_a, price_b = 150, 170
quality_a, quality_b = 4, 3
delivery_radius_a = delivery_radius_b = 6

distance_a = np.sqrt((customers_x - restaurant_a[0])**2 + (customers_y - restaurant_a[1])**2)
distance_b = np.sqrt((customers_x - restaurant_b[0])**2 + (customers_y - restaurant_b[1])**2)

delivery_available_a = distance_a <= delivery_radius_a
delivery_available_b = distance_b <= delivery_radius_b
delivery_cost_a = price_a + (10 + 2 * distance_a) - 5 * quality_a
delivery_cost_b = price_b + (10 + 2 * distance_b) - 5 * quality_b

effective_cost_a = price_a + 10 * distance_a - 5 * quality_a
effective_cost_b = price_b + 10 * distance_b - 5 * quality_b

best_cost_a = np.where(delivery_available_a, np.minimum(effective_cost_a, delivery_cost_a), effective_cost_a)
best_cost_b = np.where(delivery_available_b, np.minimum(effective_cost_b, delivery_cost_b), effective_cost_b)

customers_choose_a = best_cost_a < best_cost_b
customers_choose_b = best_cost_b <= best_cost_a

customers_a = np.sum(customers_choose_a)
customers_b = np.sum(customers_choose_b)
market_share_a = customers_a / NUMBER_OF_CUSTOMERS * 100
market_share_b = customers_b / NUMBER_OF_CUSTOMERS * 100

print("----- RESTAURANT RESULTS -----")
print("\nRestaurant A")
print(f"Price: ₹{price_a}\nQuality: {quality_a}/5")
print(f"Customers: {customers_a}\nMarket Share: {market_share_a:.2f}%")
print("\nRestaurant B")
print(f"Price: ₹{price_b}\nQuality: {quality_b}/5")
print(f"Customers: {customers_b}\nMarket Share: {market_share_b:.2f}%")

plt.figure(figsize=(8, 8))
plt.scatter(customers_x[customers_choose_a], customers_y[customers_choose_a],
            label="Customers → Restaurant A", alpha=0.6)
plt.scatter(customers_x[customers_choose_b], customers_y[customers_choose_b],
            label="Customers → Restaurant B", alpha=0.6)
plt.scatter(*restaurant_a, marker="s", s=150, label="Restaurant A")
plt.scatter(*restaurant_b, marker="s", s=150, label="Restaurant B")

for name, cx, cy, _, _ in ANCHORS:
    plt.scatter(cx, cy, marker="*", s=250, color="black")
    plt.annotate(name, (cx, cy), textcoords="offset points", xytext=(6, 6))

plt.xlim(0, TOWN_SIZE)
plt.ylim(0, TOWN_SIZE)
plt.xlabel("X Location")
plt.ylabel("Y Location")
plt.title("Restaurant Location Game - Clustered Demand")
plt.grid(True)
plt.legend()
plt.show()