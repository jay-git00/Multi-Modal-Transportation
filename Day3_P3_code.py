from pulp import LpMinimize, LpProblem, LpVariable, lpSum, PULP_CBC_CMD

# feasible routes
routes = {

    ('Visakhapatnam_Seaport', 'Singapore_Seaport'): {'cost': 500, 'time': 3},
    ('Singapore_Seaport', 'Tokyo_Seaport'): {'cost': 800, 'time': 4},
    ('Visakhapatnam_Seaport', 'Tokyo_Seaport'): {'cost': 1000, 'time': 6},
    ('Shanghai_Warehouse', 'Shanghai_Airport'): {'cost': 250, 'time': 1},
    ('Shanghai_Airport', 'Visakhapatnam_Airport'): {'cost': 500, 'time': 1},
    ('Shanghai_Airport', 'Singapore_Airport'): {'cost': 500, 'time': 1},
    ('Singapore_Airport', 'Singapore_Seaport'): {'cost': 250, 'time': 1},
    ('Singapore_Seaport', 'Tokyo_Seaport'): {'cost': 550, 'time': 3},
    ('Tokyo_Seaport', 'Tokyo_Warehouse'): {'cost': 300, 'time': 1},
    ('Shanghai_Airport', 'Tokyo Airport'): {'cost': 600, 'time': 1},
    ('Tokyo_Airport', 'Tokyo Warehouse'): {'cost': 200, 'time': 1},
    ('Dubai_Seaport', 'Singapore_Seaport'): {'cost': 600, 'time': 5},
    ('Singapore_Seaport', 'Visakhapatnam_Seaport'): {'cost': 600, 'time': 3},
    ('Dubai_Seaport', 'Visakhapatnam_Seaport'): {'cost': 1200, 'time': 8},
}

#  desired origins and destinations for each good
goods = {
    1: {'name': 'Seafood', 'origin': 'Visakhapatnam_Seaport', 'destination': 'Tokyo_Seaport', 'volume': 500,
        'order_date': 0, 'deadline': 7},
    2: {'name': 'Medicines', 'origin': 'Shanghai_Warehouse', 'destination': 'Visakhapatnam_Airport', 'volume': 400,
        'order_date': 1, 'deadline': 6},
    3: {'name': 'Crude Oil', 'origin': 'Dubai_Seaport', 'destination': 'Visakhapatnam_Seaport', 'volume': 350,
        'order_date': 0, 'deadline': 8},
}

# Creating the optimization problem
problem = LpProblem("Multi_Modal_Optimization", LpMinimize)

# Decision variables: Binary variables for each route used by each good
x = LpVariable.dicts("Route", [(g, i, j) for g in goods for (i, j) in routes], cat="Binary")

# Objective function: Minimize total cost
problem += lpSum(
    routes[(i, j)]['cost'] * x[g, i, j]  # Cost for each route
    for g in goods
    for (i, j) in routes
), "Total_Cost"

# Constraints

# 1. Each good must travel from its origin to its destination, with intermediate steps
for g in goods:
    origin = goods[g]['origin']
    destination = goods[g]['destination']

    # to ensure each good departs from its origin
    problem += lpSum(
        x[g, i, j] for (i, j) in routes if i == origin
    ) == 1, f"Origin_Constraint_{g}"


    # to ensure each good arrives at its destination (via intermediate cities)
    problem += lpSum(
        x[g, i, j] for (i, j) in routes if j == destination
    ) == 1, f"Destination_Constraint_{g}"

# 2. Delivery deadlines: each good should arrive before or on its deadline
for g in goods:
    deadline = goods[g]['deadline']

    # to ensure goods are delivered on time
    problem += lpSum(
        x[g, i, j] * routes[(i, j)]['time'] for (i, j) in routes
    ) <= deadline, f"Deadline_Constraint_{g}"



# 3. Route capacity constraints (for simplicity we assume each route has a max capacity)
route_capacity = {
    ('Visakhapatnam_Seaport', 'Singapore_Seaport'): 1000,
    ('Singapore_Seaport', 'Tokyo_Seaport'): 1400,
    ('Visakhapatnam_Seaport', 'Tokyo_Seaport'): 1200,
    ('Shanghai_Warehouse', 'Shanghai_Airport'): 1000 ,
    ('Shanghai_Airport', 'Visakhapatnam_Airport'): 1200,
    ('Shanghai_Airport', 'Singapore_Airport'): 1000,
    ('Singapore_Airport', 'Singapore_Seaport'):1600 ,
    ('Singapore_Seaport', 'Tokyo_Seaport'): 1500,
    ('Tokyo_Seaport', 'Tokyo_Warehouse'):1000 ,
    ('Shanghai_Airport', 'Tokyo Airport'):1500 ,
    ('Tokyo_Airport', 'Tokyo Warehouse'): 900,
    ('Dubai_Seaport', 'Singapore_Seaport'): 1600,
    ('Singapore_Seaport', 'Visakhapatnam_Seaport'):1500 ,
    ('Dubai_Seaport', 'Visakhapatnam_Seaport'): 1800,
}

# Ensuring no route exceeds its capacity
for (i, j) in routes:
    problem += lpSum(
        goods[g]['volume'] * x[g, i, j] for g in goods
    ) <= route_capacity[(i, j)], f"Capacity_Constraint_{i}_{j}"

# Solving the problem with minimal output
problem.solve(PULP_CBC_CMD(msg=False))

# Output results
print("Status:", problem.status)
print("Optimal Cost:", problem.objective.value())
print("Route Selection:")
for g in goods:
    print(f"\nFor Good {g} ({goods[g]['name']}):")
    for (i, j) in routes:
        if x[g, i, j].value() == 1:
            print(f"Good {g} ({goods[g]['name']}) travels from {i} to {j} on this route")
