from typing import Tuple, Union, List
from copy import copy

import numpy as np

from CFD.mesh.FluidMechanicsCalculator import FluidMechanicsCalculator
from CFD.utilities.atmosphere import AtmosphereModel


class BoundaryLayerCalculator:
    @staticmethod
    def calculate_first_layer_thickness(rho: float, 
                                        mu: float, 
                                        u_fric: float, 
                                        y_plus: float) -> float:
        """
        Calculate the thickness of the first layer.
        Parameters:
        - rho (float): Density of the fluid.
        - mu (float): Dynamic viscosity of the fluid.
        - u_fric (float): Friction velocity.
        - y_plus (float): y+ value.
        Returns:
        - float: Thickness of the first layer.
        """
        return y_plus * mu / (u_fric * rho)

    @staticmethod
    def find_first_layer_thickness(alt_m: float, 
                                   u_inf: float, 
                                   L: float, 
                                   y_plus: np.ndarray) -> np.ndarray:
        """
        Find the thickness of the first layer.
        Parameters:
        - alt_m (float): Altitude in meters.
        - u_inf (float): Free-stream velocity.
        - L (float): Characteristic length.
        - y_plus (np.ndarray): Array of y+ values.
        Returns:
        - np.ndarray: Array of first layer thickness.
        """
        atm = AtmosphereModel(alt_m)
        rho, mu = atm.density, atm.dynamic_viscosity
        re = FluidMechanicsCalculator.calculate_reynolds_number(rho, mu, u_inf, L)
        Cf = FluidMechanicsCalculator.calculate_friction_coefficient(re)
        tau_wall = FluidMechanicsCalculator.calculate_wall_shear(rho, u_inf, Cf)
        u_fric = FluidMechanicsCalculator.calculate_fric(rho, tau_wall)
        return BoundaryLayerCalculator.calculate_first_layer_thickness(rho, mu, u_fric, y_plus)

    @staticmethod
    def find_transition_x(rho: float, 
                          mu: float, 
                          u_inf: float, 
                          re_transition: float = 500000) -> float:
        """
        Find the transition location.
        Parameters:
        - rho (float): Density of the fluid.
        - mu (float): Dynamic viscosity of the fluid.
        - u_inf (float): Free-stream velocity.
        - re_transition (float): Reynolds number for transition.
        Returns:
        - float: Transition location.
        """
        return re_transition * mu / (rho * u_inf)

    @staticmethod
    def calculate_bl_thickness_laminar(re: float, 
                                       x_loc: float) -> float:
        """
        Calculate laminar boundary layer thickness.
        Parameters:
        - re (float): Reynolds number.
        - x_loc (float): Location in the streamwise direction.
        Returns:
        - float: Laminar boundary layer thickness.
        """
        return 5 * x_loc / np.sqrt(re)

    @staticmethod
    def calculate_bl_thickness_turbulent(re: float, 
                                         x_loc: float) -> float:
        """
        Calculate turbulent boundary layer thickness.
        Parameters:
        - re (float): Reynolds number.
        - x_loc (float): Location in the streamwise direction.
        Returns:
        - float: Turbulent boundary layer thickness.
        """
        return 0.37 * x_loc / re ** 0.2

    @staticmethod
    def calculate_bl_auto(rho: float, 
                          mu: float, 
                          u_inf: float, 
                          x_loc: float, 
                          re: float, 
                          re_transition: float = 500000) -> float:
        """
        Calculate boundary layer thickness automatically based on transition.
        Parameters:
        - rho (float): Density of the fluid.
        - mu (float): Dynamic viscosity of the fluid.
        - u_inf (float): Free-stream velocity.
        - x_loc (float): Location in the streamwise direction.
        - re (float): Reynolds number.
        - re_transition (float): Reynolds number for transition.
        Returns:
        - float: Boundary layer thickness.
        """
        x_transition = BoundaryLayerCalculator.find_transition_x(rho, mu, u_inf, re_transition)
        return (BoundaryLayerCalculator.calculate_bl_thickness_turbulent(re, x_loc)
                if x_loc >= x_transition
                else BoundaryLayerCalculator.calculate_bl_thickness_laminar(re, x_loc))

    @staticmethod
    def calculate_total_number_of_layers(delta_s: Union[float, np.ndarray], 
                                         delta: float, 
                                         growth_factor: float = 1.2) -> Tuple[np.ndarray, 
                                                                              List[np.ndarray]]:
        """
        Calculate the total number of boundary layers.
        Parameters:
        - delta_s (float): First layer thickness.
        - delta (float): Total boundary layer thickness.
        - growth_factor (float): Growth factor for each layer.
        Returns:
        - Tuple[float, np.ndarray]: Total thickness and array of layer thicknesses.
        """
        if isinstance(delta_s, (int, float)):
            delta_s = np.array([delta_s])
        curr_thickness = []
        thickness = []
        for curr_delta_s in delta_s:
            thickness_temp = [0, curr_delta_s]
            total_thickness_temp = copy(curr_delta_s)
            while total_thickness_temp <= delta:
                curr_thickness_temp = thickness_temp[-1] * growth_factor
                thickness_temp.append(curr_thickness_temp)
                total_thickness_temp += curr_thickness_temp
            curr_thickness.append(curr_thickness_temp)
            thickness.append(np.array(thickness_temp, dtype=object))
        return np.array(curr_thickness, dtype=object), thickness

    @staticmethod
    def calculate_growth_rate_for_layers(delta_s: Union[float, np.ndarray], 
                                         delta: float, 
                                         total_layers: int,
                                         growth_factor: float = 1.3, 
                                         increment: float = 0.1) -> Tuple[np.ndarray, 
                                                                          List[np.ndarray], 
                                                                          np.ndarray]:
        """
        Calculate growth rate for boundary layer layers.
        Parameters:
        - delta_s (Union[float, np.ndarray]): Array of initial layer thicknesses.
        - delta (float): Boundary layer thickness.
        - total_layers (int): Total number of layers.
        - growth_factor (float, optional): Initial growth factor. Defaults to 1.3.
        - increment (float, optional): Increment for growth factor adjustment. Defaults to 0.1.
        Returns:
        - Tuple[np.ndarray, List[np.ndarray], np.ndarray]: Current thickness, thickness array, growth factor array.
        """
        if isinstance(delta_s, (int, float)):
            delta_s = np.array([delta_s])
        curr_thickness = []
        thickness = []
        growth_factor_array = []
        for curr_delta_s in delta_s:
            not_found_growth = True
            while not_found_growth:
                thickness_temp = [0, curr_delta_s]
                total_thickness_temp = copy(curr_delta_s)
                while total_thickness_temp <= delta:
                    curr_thickness_temp = thickness_temp[-1] * growth_factor
                    thickness_temp.append(curr_thickness_temp)
                    total_thickness_temp += curr_thickness_temp
                if len(thickness_temp) > total_layers:
                    growth_factor += increment
                    increment *= 0.9
                elif len(thickness_temp) < total_layers:
                    growth_factor -= increment
                    increment *= 0.9
                else:
                    not_found_growth = False
            curr_thickness.append(curr_thickness_temp)
            thickness.append(np.array(thickness_temp, dtype=object))
            growth_factor_array.append(growth_factor)
        return np.array(curr_thickness, dtype=object), thickness, np.array(growth_factor_array, dtype=object)

    @staticmethod
    def calculate_bl_values(alt_m: float, 
                            u_inf: float, 
                            L: float, 
                            x_loc: float, 
                            re_transition: float = 500000) -> Tuple[float, 
                                                                    float, 
                                                                    float, 
                                                                    float, 
                                                                    float, 
                                                                    float, 
                                                                    float]:
        """
        Calculate boundary layer values.
        Parameters:
        - alt_m (float): Altitude in meters.
        - u_inf (float): Freestream velocity.
        - L (float): Characteristic length.
        - x_loc (float): Streamwise location.
        - re_transition (float, optional): Reynolds number for transition. Defaults to 500000.
        Returns:
        - Tuple[float, float, float, float, float, float, float]: Delta, friction velocity, wall shear stress, friction coefficient, Reynolds number, density, dynamic viscosity.
        """
        atm = AtmosphereModel(alt_m)
        rho, mu = atm.density, atm.dynamic_viscosity
        re = FluidMechanicsCalculator.calculate_reynolds_number(rho, mu, u_inf, L)
        Cf = FluidMechanicsCalculator.calculate_friction_coefficient(re)
        tau_wall = FluidMechanicsCalculator.calculate_wall_shear(rho, u_inf, Cf)
        u_fric = FluidMechanicsCalculator.calculate_fric(rho, tau_wall)
        delta = BoundaryLayerCalculator.calculate_bl_auto(rho, mu, u_inf, x_loc, re, re_transition)
        return delta, u_fric, tau_wall, Cf, re, rho, mu

    @staticmethod
    def find_layers(alt_m: float, 
                    u_inf: float, 
                    L: float, 
                    y_plus: np.ndarray, 
                    x_loc: float, 
                    re_transition: float = 500000, 
                    growth_factor: float = 1.2) -> Tuple[np.ndarray, 
                                                         List[np.ndarray], 
                                                         float, 
                                                         np.ndarray]:
        """
        Find the total thickness and array of layer thicknesses.
        Parameters:
        - alt_m (float): Altitude in meters.
        - u_inf (float): Free-stream velocity.
        - L (float): Characteristic length.
        - y_plus (np.ndarray): Array of y+ values.
        - x_loc (float): Location in the streamwise direction.
        - re_transition (float): Reynolds number for transition.
        - growth_factor (float): Growth factor for each layer.
        Returns:
        - Tuple[float, np.ndarray, float, float]: Total thickness, array of layer thicknesses, boundary layer thickness, first layer thickness.
        """
        delta, u_fric, tau_wall, Cf, re, rho, mu = BoundaryLayerCalculator.calculate_bl_values(alt_m, u_inf, L, x_loc, re_transition)
        delta_s = BoundaryLayerCalculator.calculate_first_layer_thickness(rho, mu, u_fric, y_plus)
        total_thickness, thickness = BoundaryLayerCalculator.calculate_total_number_of_layers(delta_s, delta, growth_factor)
        return total_thickness, thickness, delta, delta_s

    @staticmethod
    def find_layers_given_first_layer(alt_m: float, 
                                      u_inf: float, 
                                      L: float, 
                                      delta_s: np.ndarray, 
                                      x_loc: float, 
                                      re_transition: float = 500000, 
                                      growth_factor: float = 1.2) -> Tuple[np.ndarray, 
                                                                           List[np.ndarray], 
                                                                           float, 
                                                                           np.ndarray]:
        """
        Calculate boundary layer properties based on the first layer thickness.
        Parameters:
        - alt_m (float): Altitude in meters.
        - u_inf (float): Freestream velocity.
        - L (float): Characteristic length.
        - delta_s (np.ndarray): Array of first layer thicknesses.
        - x_loc (float): Streamwise location.
        - re_transition (float, optional): Reynolds number for transition. Defaults to 500000.
        - growth_factor (float, optional): Growth factor for total number of layers. Defaults to 1.2.
        Returns:
        - Tuple[np.ndarray, List[np.ndarray], float, np.ndarray]: Total thickness, thickness, delta, y_plus
        """
        if isinstance(delta_s, float):
            delta_s = np.array([delta_s])
        delta, u_fric, tau_wall, Cf, re, rho, mu = BoundaryLayerCalculator.calculate_bl_values(alt_m, u_inf, L, x_loc, re_transition)
        y_plus = FluidMechanicsCalculator.calculate_y_plus(delta_s, u_fric, rho, mu)
        total_thickness, thickness = BoundaryLayerCalculator.calculate_total_number_of_layers(delta_s, delta, growth_factor)
        return total_thickness, thickness, delta, y_plus

    @staticmethod
    def find_layers_given_num_of_layers(alt_m: float, 
                                        u_inf: float, 
                                        L: float, 
                                        y_plus: np.ndarray, 
                                        x_loc: float, 
                                        total_num_of_layers: int, 
                                        delta_s = None,
                                        re_transition: float = 500000, 
                                        growth_factor: float = 1.2, 
                                        increment: float = 0.1) -> Tuple[np.ndarray, 
                                                                         List[np.ndarray], 
                                                                         np.ndarray, 
                                                                         float, 
                                                                         np.ndarray]:
        """
        Calculate boundary layer properties based on the total number of layers.
        Parameters:
        - alt_m (float): Altitude in meters.
        - u_inf (float): Freestream velocity.
        - L (float): Characteristic length.
        - y_plus (np.ndarray): Array of non-dimensional distances from wall.
        - x_loc (float): Streamwise location.
        - total_num_of_layers (int): Total number of layers.
        - re_transition (float, optional): Reynolds number for transition. Defaults to 500000.
        - growth_factor (float, optional): Growth factor for total number of layers. Defaults to 1.2.
        - increment (float, optional): Increment for growth factor calculation. Defaults to 0.1.
        Returns:
        - Tuple[np.ndarray, List[np.ndarray], np.ndarray, float, np.ndarray]: Total thickness, thickness, growth_factor_used, delta, delta_s
        """
        delta, u_fric, tau_wall, Cf, re, rho, mu = BoundaryLayerCalculator.calculate_bl_values(alt_m, u_inf, L, x_loc, re_transition)
        if delta_s is None:
            delta_s = BoundaryLayerCalculator.calculate_first_layer_thickness(rho, mu, u_fric, y_plus)
        total_thickness, thickness, growth_factor_used = BoundaryLayerCalculator.calculate_growth_rate_for_layers(
            delta_s, delta, total_num_of_layers, growth_factor, increment)
        return total_thickness, thickness, growth_factor_used, delta, delta_s


def main():
    """
    Main function to demonstrate the usage of boundary layer calculations.
    """
    alt = 0
    u_inf = 1735
    L = 5.825
    # y_plus = 1
    y_plus = np.array([1, 5, 30])
    delta_s = 3.1595e-5 * np.array([0.75, 1, 1.25, 1.5, 1.75, 2.0])
    total_layers = 35
    boundary_layer_calculator = BoundaryLayerCalculator()

    # total_thickness, thickness, delta, delta_s = boundary_layer_calculator.find_layers(alt, u_inf, L, y_plus, L)
    # print(total_thickness)
    # for th in thickness:
    #     print(len(th))
    # print(thickness)
    # print(delta)
    # print(delta_s)

    # total_thickness, thickness, delta, y_plus = boundary_layer_calculator.find_layers_given_first_layer(alt, u_inf, L, delta_s, L, growth_factor=1.4)
    # print(y_plus)
    # print(total_thickness)
    # for th in thickness:
    #     print(len(th))

    total_thickness, thickness, growth_factor_used, delta, delta_s = boundary_layer_calculator.find_layers_given_num_of_layers(
        alt, u_inf, L, y_plus, L, total_layers)
    print(total_thickness)
    ind = 0
    for th in thickness:
        print(len(th))
        print(growth_factor_used[ind])
        ind += 1
    print(thickness)
    print(delta)
    print(delta_s)


if __name__ == "__main__":
    main()