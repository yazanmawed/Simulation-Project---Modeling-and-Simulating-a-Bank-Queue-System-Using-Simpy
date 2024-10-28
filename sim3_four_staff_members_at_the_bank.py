import simpy
import random
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#parameters for the simulation
RANDOM_SEED = 42
NUM_STAFF = 4   # number of bank staff
SERVICE_TIME = 4  # average service time in minutes
ARRIVAL_RATE = 2  # one customer every 2 minutes
SIM_TIME = 60     # simulation time in minutes
APPOINTMENT_PROBABILITY = 0.3  # probability a customer has an appointment

wait_times_appointment = []
wait_times_non_appointment = []
service_times_appointment = []
service_times_non_appointment = []
arrival_times = []
served_customers = []
served_customers_type = []

def customer(env, name, bank, service_time, customer_num, appointment):
    arrival_time = env.now
    arrival_times.append(arrival_time)
    priority = 0 if appointment else 1
    print(f'{name} arrives at the bank at {arrival_time:.2f} minutes. Appointment: {appointment}')
    
    with bank.request(priority=priority) as request:
        yield request
        
        wait_time = env.now - arrival_time
        if appointment:
            wait_times_appointment.append(wait_time)
        else:
            wait_times_non_appointment.append(wait_time)
        
        served_customers.append(customer_num)
        served_customers_type.append("Appointment" if appointment else "Walk-in")
        print(f'{name} starts service at {env.now:.2f} minutes after waiting for {wait_time:.2f} minutes.')
        
        actual_service_time = random.expovariate(1.0 / service_time)
        if appointment:
            service_times_appointment.append(actual_service_time)
        else:
            service_times_non_appointment.append(actual_service_time)
        
        yield env.timeout(actual_service_time)
        print(f'{name} leaves the bank at {env.now:.2f} minutes.')

def customer_generator(env, bank, arrival_rate, service_time):
    customer_count = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / arrival_rate))
        customer_count += 1
        has_appointment = random.random() < APPOINTMENT_PROBABILITY
        env.process(customer(env, f'Customer {customer_count}', bank, service_time, customer_count, has_appointment))

def run_simulation(num_staff, service_time, arrival_rate, sim_time):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    bank = simpy.PriorityResource(env, num_staff)
    env.process(customer_generator(env, bank, arrival_rate, service_time))
    env.run(until=sim_time)

# Plotting function
def plot_simulation_results():
    plt.figure()
    plt.scatter(
        [i for i, t in zip(served_customers, served_customers_type) if t == "Appointment"],
        wait_times_appointment, color='blue', edgecolor='black', label="Appointment"
    )
    plt.scatter(
        [i for i, t in zip(served_customers, served_customers_type) if t == "Walk-in"],
        wait_times_non_appointment, color='red', edgecolor='black', label="Walk-in"
    )
    plt.title('Customer Number vs. Waiting Time (Booked appointments)')
    plt.xlabel('Customer Number')
    plt.ylabel('Waiting Time (minutes)')
    plt.grid(True)
    plt.legend()
    plt.savefig('waiting_time_plot_priority.png')

    plt.figure()
    plt.scatter(
        [i for i, t in zip(served_customers, served_customers_type) if t == "Appointment"],
        service_times_appointment, color='blue', edgecolor='black', label="Appointment"
    )
    plt.scatter(
        [i for i, t in zip(served_customers, served_customers_type) if t == "Walk-in"],
        service_times_non_appointment, color='red', edgecolor='black', label="Walk-in"
    )
    plt.title('Customer Number vs. Service Time (Booked appointments)')
    plt.xlabel('Customer Number')
    plt.ylabel('Service Time (minutes)')
    plt.grid(True)
    plt.legend()
    plt.savefig('service_time_plot_priority.png')

print('Starting bank queue simulation with priority queue...')
run_simulation(NUM_STAFF, SERVICE_TIME, ARRIVAL_RATE, SIM_TIME)
plot_simulation_results()
