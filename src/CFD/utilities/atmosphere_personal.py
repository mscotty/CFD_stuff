import math

class Atmosphere:
    """
    A class to compute various properties of the atmosphere based on altitude.
    """

    # Constants
    R = 287.05  # Specific gas constant for dry air, J/(kg·K)
    g0 = 9.80665  # Standard gravity, m/s²
    gamma = 1.4  # Ratio of specific heats for dry air
    p0 = 101325  # Sea level standard atmospheric pressure, Pa
    T0 = 288.15  # Sea level standard temperature, K
    rho0 = 1.225  # Sea level standard density, kg/m³
    S = 110.4  # Sutherland's constant, K

    # Troposphere constants
    L = -0.0065  # Temperature lapse rate, K/m

    def __init__(self, altitude):
        self.altitude = altitude  # Altitude in meters
        self.temperature = self.calculate_temperature()
        self.pressure = self.calculate_pressure()
        self.density = self.calculate_density()
        self.speed_of_sound = self.calculate_speed_of_sound()
        self.dynamic_viscosity = self.calculate_dynamic_viscosity()
        self.kinematic_viscosity = self.calculate_kinematic_viscosity()
        self.Cp = self.calculate_Cp()
        self.Cv = self.calculate_Cv()

    def calculate_temperature(self):
        """
        Calculate the temperature at the given altitude using the International Standard Atmosphere (ISA) model.
        """
        if self.altitude <= 11000:  # Troposphere
            temperature = self.T0 + self.L * self.altitude
        else:
            # For altitudes above 11 km, we'll assume a simplified model where temperature remains constant
            temperature = self.T0 + self.L * 11000
        return temperature

    def calculate_pressure(self):
        """
        Calculate the pressure at the given altitude using the International Standard Atmosphere (ISA) model.
        """
        if self.altitude <= 11000:  # Troposphere
            pressure = self.p0 * (1 + self.L * self.altitude / self.T0) ** (-self.g0 / (self.R * self.L))
        else:
            # For altitudes above 11 km, we'll assume a simplified model where pressure follows an exponential decrease
            pressure = self.p0 * (1 + self.L * 11000 / self.T0) ** (-self.g0 / (self.R * self.L)) * math.exp(
                -self.g0 * (self.altitude - 11000) / (self.R * self.calculate_temperature()))
        return pressure

    def calculate_density(self):
        """
        Calculate the air density at the given altitude using the International Standard Atmosphere (ISA) model.
        """
        density = self.pressure / (self.R * self.calculate_temperature())
        return density

    def calculate_speed_of_sound(self):
        """
        Calculate the speed of sound at the given altitude using the International Standard Atmosphere (ISA) model.
        """
        speed_of_sound = math.sqrt(self.gamma * self.R * self.calculate_temperature())
        return speed_of_sound

    def calculate_dynamic_viscosity(self):
        """
        Calculate the dynamic viscosity at the given altitude using Sutherland's formula.
        """
        T = self.calculate_temperature()
        dynamic_viscosity = 1.458e-6 * (T ** 1.5) / (T + self.S)
        return dynamic_viscosity

    def calculate_kinematic_viscosity(self):
        """
        Calculate the kinematic viscosity at the given altitude.
        """
        kinematic_viscosity = self.dynamic_viscosity / self.density
        return kinematic_viscosity

    def calculate_Cp(self):
        """
        Calculate the specific heat at constant pressure at the given altitude.
        """
        Cp = self.gamma * self.R / (self.gamma - 1)
        return Cp

    def calculate_Cv(self):
        """
        Calculate the specific heat at constant volume at the given altitude.
        """
        Cv = self.R / (self.gamma - 1)
        return Cv

    def __str__(self):
        return (f"Altitude: {self.altitude} m\n"
                f"Temperature: {self.temperature:.2f} K\n"
                f"Pressure: {self.pressure:.2f} Pa\n"
                f"Density: {self.density:.4f} kg/m³\n"
                f"Speed of Sound: {self.speed_of_sound:.2f} m/s\n"
                f"Dynamic Viscosity: {self.dynamic_viscosity:.6e} Pa·s\n"
                f"Kinematic Viscosity: {self.kinematic_viscosity:.6e} m²/s\n"
                f"Cp: {self.Cp:.2f} J/(kg·K)\n"
                f"Cv: {self.Cv:.2f} J/(kg·K)")

# Example usage
altitude = 5000  # Altitude in meters
atmosphere = Atmosphere(altitude)
print(atmosphere)
