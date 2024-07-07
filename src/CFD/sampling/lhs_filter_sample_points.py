import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from pyDOE2 import lhs


# Standard atmosphere model (simplified)
def get_air_density_and_speed_of_sound(altitude):
    """
    Calculate the air density and speed of sound based on altitude.

    @param altitude Altitude in meters.
    @return Tuple of air density (kg/m^3) and speed of sound (m/s).
    """
    if altitude <= 11000:
        # Troposphere approximation
        T0 = 288.15  # Sea-level standard temperature (K)
        P0 = 101325  # Sea-level standard pressure (Pa)
        R = 287.05  # Specific gas constant for dry air (J/(kg·K))
        g = 9.80665  # Acceleration due to gravity (m/s^2)
        L = 0.0065  # Temperature lapse rate (K/m)

        T = T0 - L * altitude
        P = P0 * (1 - L * altitude / T0) ** (g / (R * L))
        rho = P / (R * T)
        a = np.sqrt(1.4 * R * T)
    else:
        # Simple approximation for stratosphere and above (up to 20km)
        rho = 0.36391  # Density at 20km altitude (kg/m^3)
        a = 295.07  # Speed of sound at 20km altitude (m/s)

    return rho, a


# Latin Hypercube Sampling for aerodynamic conditions
def generate_sample_points(n_samples, ranges):
    """
    Generate sample points using Latin Hypercube Sampling.

    @param n_samples Number of sample points to generate.
    @param ranges List of tuples representing the range (min, max) for each variable.
    @return Array of generated sample points.
    """
    # Create LHS samples
    lhs_samples = lhs(len(ranges), samples=n_samples)

    # Scale samples to the provided ranges
    samples = np.zeros_like(lhs_samples)
    for i, (low, high) in enumerate(ranges):
        samples[:, i] = lhs_samples[:, i] * (high - low) + low

    return samples


# Filter sample points based on Mach and dynamic pressure
def filter_sample_points(samples, mach_range, q_range):
    """
    Filter sample points based on Mach number and dynamic pressure.

    @param samples Array of sample points to filter.
    @param mach_range Tuple representing the range (min, max) for Mach number.
    @param q_range Tuple representing the range (min, max) for dynamic pressure (Pa).
    @return Array of filtered sample points.
    """
    filtered_points = []
    for point in samples:
        mach = point[0]
        altitude = point[1]

        rho, a = get_air_density_and_speed_of_sound(altitude)
        dynamic_pressure = 0.5 * rho * (mach * a) ** 2

        if mach_range[0] <= mach <= mach_range[1] and q_range[0] <= dynamic_pressure <= q_range[1]:
            filtered_points.append(point)

    return np.array(filtered_points)


# Main function to generate the desired number of valid points
def get_valid_sample_points(desired_n_samples, ranges, mach_range, q_range, batch_size=1000):
    """
    Generate the desired number of valid sample points by iteratively sampling and filtering.

    @param desired_n_samples Desired number of valid sample points.
    @param ranges List of tuples representing the range (min, max) for each variable.
    @param mach_range Tuple representing the range (min, max) for Mach number.
    @param q_range Tuple representing the range (min, max) for dynamic pressure (Pa).
    @param batch_size Number of sample points to generate in each batch.
    @return Array of valid sample points.
    """
    valid_samples = []

    while len(valid_samples) < desired_n_samples:
        # Generate a batch of sample points
        samples = generate_sample_points(batch_size, ranges)

        # Filter the samples based on Mach and dynamic pressure
        filtered_samples = filter_sample_points(samples, mach_range, q_range)

        # Add the valid samples to the list
        valid_samples.extend(filtered_samples)

        print(f"Generated {len(valid_samples)} valid samples so far.")

    # Truncate to the desired number of samples
    valid_samples = np.array(valid_samples)[:desired_n_samples]

    return valid_samples


# Example ranges for LHS (mach, altitude, alpha, beta, deflection_yaw, deflection_pitch, deflection_roll)
ranges = [
    (0.3, 2.0),  # Mach range
    (0, 20000),  # Altitude range (meters)
    (-5, 15),  # Angle of attack (degrees)
    (-5, 5),  # Sideslip angle (degrees)
    (-20, 20),  # Deflection in yaw (degrees)
    (-20, 20),  # Deflection in pitch (degrees)
    (-20, 20)  # Deflection in roll (degrees)
]

# Define the desired number of valid samples
desired_n_samples = 100

# Define the desired Mach and dynamic pressure ranges
mach_range = (0.5, 1.5)
q_range = (5000, 30000)  # Example dynamic pressure range in Pascals

# Get the valid sample points
valid_samples = get_valid_sample_points(desired_n_samples, ranges, mach_range, q_range)

# Convert to DataFrame
df_valid_samples = pd.DataFrame(valid_samples,
                                columns=['mach', 'altitude', 'alpha', 'beta', 'deflection_yaw', 'deflection_pitch',
                                         'deflection_roll'])
print(df_valid_samples)

# Save filtered samples to CSV
df_valid_samples.to_csv('filtered_aero_samples.csv', index=False)
