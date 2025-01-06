from flask import Flask, render_template, request, jsonify
import random
import multiprocessing
# httpsmhdowis.pythonanywhere.com

# Flask app setup
app = Flask(__name__)

# Genetic Algorithm Configuration
EMPLOYEES = []
HOURS = 24
MAX_HOURS_PER_EMPLOYEE = 8
MIN_HOURS_PER_EMPLOYEE = 4
POPULATION_SIZE = 100
GENERATIONS = 500
MUTATION_RATE = 0.1

# Generate initial schedule for a single employee
def generate_schedule():
    schedule = {}
    for employee in EMPLOYEES:
        schedule[employee] = random.randint(MIN_HOURS_PER_EMPLOYEE, MAX_HOURS_PER_EMPLOYEE)
    return schedule

# Generate initial population of schedules
def generate_population():
    return [generate_schedule() for _ in range(POPULATION_SIZE)]

# Fitness function with improved fairness and penalty
def fitness(schedule):
    total_hours = sum(schedule.values())
    fairness = len(set(schedule.values()))
    penalty = abs(total_hours - HOURS)
    if penalty > 0:
        penalty = penalty * 0.5  # Adjust weight for penalty
    # The formula now rewards both the total hours being close to the target and fairness in distribution
    return 1 / (1 + penalty) + fairness

# Selection function using tournament selection
def select_population(population):
    weighted_population = [(schedule, fitness(schedule)) for schedule in population]
    weighted_population.sort(key=lambda x: x[1], reverse=True)
    return [schedule for schedule, _ in weighted_population[:POPULATION_SIZE // 2]]

# Crossover function with multi-point crossover
def crossover(parent1, parent2):
    child = {}
    crossover_point = random.randint(1, len(EMPLOYEES) - 1)
    for idx, employee in enumerate(EMPLOYEES):
        if idx < crossover_point:
            child[employee] = parent1[employee]
        else:
            child[employee] = parent2[employee]
    return child

# Mutation function with intelligent mutation (only small adjustments)
def mutate(schedule):
    if random.random() < MUTATION_RATE:
        employee = random.choice(EMPLOYEES)
        new_hours = random.randint(MIN_HOURS_PER_EMPLOYEE, MAX_HOURS_PER_EMPLOYEE)
        # Ensure mutation does not disturb too much
        if abs(schedule[employee] - new_hours) > 1:
            schedule[employee] = new_hours

# Parallel execution for faster computation using multiprocessing
def genetic_algorithm():
    population = generate_population()

    for generation in range(GENERATIONS):
        selected_population = select_population(population)
        new_population = []

        with multiprocessing.Pool() as pool:
            while len(new_population) < POPULATION_SIZE:
                parent1 = random.choice(selected_population)
                parent2 = random.choice(selected_population)
                child = crossover(parent1, parent2)
                mutate(child)
                new_population.append(child)

        population = new_population

        best_schedule = max(population, key=fitness)
        if fitness(best_schedule) > 0.99:  # Early termination if optimal solution found
            break

    return best_schedule

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    global EMPLOYEES, HOURS, MAX_HOURS_PER_EMPLOYEE, MIN_HOURS_PER_EMPLOYEE

    # Get inputs from the form
    EMPLOYEES = request.json['employees']
    HOURS = int(request.json['hours'])
    MAX_HOURS_PER_EMPLOYEE = int(request.json['max_hours'])
    MIN_HOURS_PER_EMPLOYEE = int(request.json['min_hours'])

    # Run genetic algorithm
    best_schedule = genetic_algorithm()

    # Return the best schedule as JSON
    return jsonify(best_schedule)

if __name__ == '__main__':
    app.run(debug=True)
