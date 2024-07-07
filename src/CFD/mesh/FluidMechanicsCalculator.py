import numpy as np


class FluidMechanicsCalculator:
    @staticmethod
    def calculate_reynolds_number(rho: float, mu: float, u_inf: float, L: float) -> float:
        """
        Calculate Reynolds number.

        Parameters:
        - rho (float): Density of the fluid.
        - mu (float): Dynamic viscosity of the fluid.
        - u_inf (float): Free-stream velocity.
        - L (float): Characteristic length.

        Returns:
        - float: Reynolds number.
        """
        return rho * u_inf * L / mu

    @staticmethod
    def calculate_friction_coefficient(re: float) -> float:
        """
        Calculate friction coefficient using the power-law formula.

        Parameters:
        - re (float): Reynolds number.

        Returns:
        - float: Friction coefficient.
        """
        return 0.026 / re ** (1 / 7)

    @staticmethod
    def calculate_wall_shear(rho: float, u_inf: float, Cf: float) -> float:
        """
        Calculate wall shear stress.

        Parameters:
        - rho (float): Density of the fluid.
        - u_inf (float): Free-stream velocity.
        - Cf (float): Friction coefficient.

        Returns:
        - float: Wall shear stress.
        """
        return Cf * rho * u_inf ** 2 / 2

    @staticmethod
    def calculate_fric(rho: float, tau_wall: float) -> float:
        """
        Calculate friction velocity.

        Parameters:
        - rho (float): Density of the fluid.
        - tau_wall (float): Wall shear stress.

        Returns:
        - float: Friction velocity.
        """
        return np.sqrt(tau_wall / rho)

    @staticmethod
    def calculate_y_plus(delta_s, u_fric: float, rho: float, mu: float):
        """
        Calculate the nondimensional distance from the wall (y+).

        Parameters:
        - delta_s (float): Local boundary layer thickness.
        - u_fric (float): Friction velocity.
        - rho (float): Density of the fluid.
        - mu (float): Dynamic viscosity of the fluid.

        Returns:
        - float: Nondimensional distance from the wall.
        """
        return delta_s * u_fric * rho / mu

