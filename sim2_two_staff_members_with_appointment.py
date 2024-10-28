import simpy
import random
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# parameters for the simulation
RANDOM_SEED = 42 
NUM_STAFF = 4   # number of bank staff
SERVICE_TIME = 4  # average service time in minutes
ARRIVAL_RATE = 2  # one customer every 2 minutes
SIM_TIME = 60     # simulation time in minutes

wait_times = []
service_times = []
arrival_times = []
served_customers = []

def customer(env, name, bank, service_time, customer_num):
    arrival_time = env.now
    arrival_times.append(arrival_time)
    print(f'{name} arrives at the bank at {arrival_time:.2f} minutes.')
    
    with bank.request() as request:
        yield request
        
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)
        served_customers.append(customer_num)
        print(f'{name} starts service at {env.now:.2f} minutes after waiting for {wait_time:.2f} minutes.')
        
        actual_service_time = random.expovariate(1.0 / service_time)
        service_times.append(actual_service_time)
        yield env.timeout(actual_service_time)
        print(f'{name} leaves the bank at {env.now:.2f} minutes.')

def customer_generator(env, bank, arrival_rate, service_time):
    customer_count = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / arrival_rate))
        customer_count += 1
        env.process(customer(env, f'Customer {customer_count}', bank, service_time, customer_count))

def run_simulation(num_staff, service_time, arrival_rate, sim_time):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    bank = simpy.Resource(env, num_staff)
    env.process(customer_generator(env, bank, arrival_rate, service_time))
    env.run(until=sim_time)

# Plotting function
def plot_simulation_results():
    plt.figure()
    plt.scatter(served_customers, wait_times, color='blue', edgecolor='black')
    plt.title('Customer Number vs. Waiting Time (Staff: 4)')
    plt.xlabel('Customer Number')
    plt.ylabel('Waiting Time (minutes)')
    plt.grid(True)
    plt.savefig('waiting_time_plot.png')

    plt.figure()
    plt.scatter(served_customers, service_times, color='green', edgecolor='black')
    plt.title('Customer Number vs. Service Time (Staff: 4)')
    plt.xlabel('Customer Number')
    plt.ylabel('Service Time (minutes)')
    plt.grid(True)
    plt.savefig('service_time_plot.png')

print('Starting bank queue simulation...')
run_simulation(NUM_STAFF, SERVICE_TIME, ARRIVAL_RATE, SIM_TIME)
plot_simulation_results()
