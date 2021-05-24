import numpy as np
import matplotlib.pyplot as plt
import random
np.random.seed(1)


# multiply and add by random numbers to get some real values
data = []

for x in range(50):
	data.append(np.random.randint(0, 20))
data[33] = 39

# Function to Detection Outlier on one-dimentional datasets.
def find_anomalies(random_data):
    #define a list to accumlate anomalies
    anomalies = []
    
    # Set upper and lower limit to 3 standard deviation
    random_data_std = np.std(random_data)
    random_data_mean = np.mean(random_data)
    anomaly_cut_off = random_data_std * 3
    
    lower_limit  = random_data_mean - anomaly_cut_off 
    upper_limit = random_data_mean + anomaly_cut_off
    print(lower_limit)
    # Generate outliers
    for outlier in random_data:
        if outlier > upper_limit or outlier < lower_limit:
            anomalies.append(outlier)
    return anomalies

print(np.std(data))
print(np.average(data))
plt.plot(data)
print(data)
find_anomalies(data)