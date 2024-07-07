import pytest
import numpy as np
from numpy import testing

from CFD.mesh.BoundaryLayerCalculator import BoundaryLayerCalculator
from CFD.mesh.FluidMechanicsCalculator import FluidMechanicsCalculator


@pytest.fixture
def atmosphere_data():
    """!
    @brief Fixture providing atmospheric data like density and dynamic viscosity.
    """
    return {'rho': 1.225,
            'mu': 1.7894e-5}


@pytest.fixture
def boundary_layer_data():
    """!
    @brief Fixture providing data related to the boundary layer calculations.
    """
    return {'alt_m': 0.0,
            'u_inf': 10.0,
            'L': 5.0,
            'x_loc': 1.0,
            're_transition': 500000,
            'growth_factor': 1.2,
            'increment': 0.1,
            'y_plus_single': 1.0,
            'y_plus_array': np.array([1.0, 5.0, 30.0]),
            'delta_s_single': 2.5e-4,
            'delta_s_array': np.array([5.0e-6, 4.0e-5, 2.5e-4]),
            'delta': 0.015,
            'total_layers': 30}


@pytest.fixture
def fluid_calculator():
    """!
    @brief Fixture providing an instance of FluidMechanicsCalculator.
    """
    return FluidMechanicsCalculator()


@pytest.fixture
def re(atmosphere_data, boundary_layer_data, fluid_calculator):
    """!
    @brief Fixture providing a Reynolds number.

    @param[in] atmosphere_data : Fixture providing atmospheric data like density and dynamic viscosity.
    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    @param[in] fluid_calculator : Fixture providing an instance of FluidMechanicsCalculator.
    """
    rho = atmosphere_data['rho']
    mu = atmosphere_data['mu']
    u_inf = boundary_layer_data['u_inf']
    L = boundary_layer_data['L']
    x_loc = boundary_layer_data['x_loc']
    return fluid_calculator.calculate_reynolds_number(rho, mu, u_inf, L*x_loc)


def test_calculate_first_layer_thickness(atmosphere_data, boundary_layer_data, fluid_calculator):
    """!
    @brief Test calculate_first_layer_thickness method of BoundaryLayerCalculator.

    @param[in] atmosphere_data : Fixture providing atmospheric data like density and dynamic viscosity.
    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    @param[in] fluid_calculator : Fixture providing an instance of FluidMechanicsCalculator.
    """
    rho = atmosphere_data['rho']
    mu = atmosphere_data['mu']
    u_fric = fluid_calculator.calculate_fric(rho, mu)
    thickness = BoundaryLayerCalculator.calculate_first_layer_thickness(rho, mu, u_fric, boundary_layer_data['y_plus_single'])
    assert thickness == pytest.approx(0.003822, abs=1e-6)


def test_find_transition_x(atmosphere_data, boundary_layer_data, re):
    """!
    @brief Test find_transition_x method of BoundaryLayerCalculator.

    @param[in] atmosphere_data : Fixture providing atmospheric data like density and dynamic viscosity.
    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    @param[in] re : Fixture providing a Reynolds number.
    """
    rho = atmosphere_data['rho']
    mu = atmosphere_data['mu']
    u_inf = boundary_layer_data['u_inf']
    transition_x = BoundaryLayerCalculator.find_transition_x(rho, mu, u_inf, re)
    assert transition_x == pytest.approx(5.0, abs=1e-1)


def test_calculate_bl_thickness_laminar(re, boundary_layer_data):
    """!
    @brief Test calculate_bl_thickness_laminar method of BoundaryLayerCalculator.

    @param[in] re : Fixture providing a Reynolds number.
    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    laminar_thickness = BoundaryLayerCalculator.calculate_bl_thickness_laminar(re, boundary_layer_data['x_loc'])
    assert laminar_thickness == pytest.approx(0.0027025, abs=1e-7)


def test_calculate_bl_thickness_turbulent(re, boundary_layer_data):
    """!
    @brief Test calculate_bl_thickness_turbulent method of BoundaryLayerCalculator.

    @param[in] re : Fixture providing a Reynolds number.
    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    turbulent_thickness = BoundaryLayerCalculator.calculate_bl_thickness_turbulent(re, boundary_layer_data['x_loc'])
    assert turbulent_thickness == pytest.approx(0.01825, abs=1e-5)


def test_calculate_bl_auto(atmosphere_data, boundary_layer_data, re):
    """!
    @brief

    @param[in] atmosphere_data : Fixture providing atmospheric data like density and dynamic viscosity.
    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    @param[in] re : Fixture providing a Reynolds number.
    """
    """
    Test calculate_bl_auto method of BoundaryLayerCalculator.
    """
    rho = atmosphere_data['rho']
    mu = atmosphere_data['mu']
    u_inf = boundary_layer_data['u_inf']
    x_loc = boundary_layer_data['x_loc']
    auto_thickness = BoundaryLayerCalculator.calculate_bl_auto(rho, mu, u_inf, x_loc, re)
    assert auto_thickness == pytest.approx(0.01825, abs=1e-5)


def test_calculate_total_number_of_layers_single(boundary_layer_data):
    """!
    @brief Test calculate_total_number_of_layers method of BoundaryLayerCalculator.

    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    u_inf = boundary_layer_data['u_inf']
    L = boundary_layer_data['L']
    alt_m = boundary_layer_data['alt_m']
    re_transition = boundary_layer_data['re_transition']
    growth_factor = boundary_layer_data['growth_factor']
    y_plus = boundary_layer_data['y_plus_single']
    x_loc = boundary_layer_data['x_loc']
    total_thickness, thickness, delta, delta_s = BoundaryLayerCalculator.find_layers(alt_m, u_inf, L, y_plus, x_loc, re_transition, growth_factor)
    for curr_total_thickness in total_thickness:
        assert np.all(curr_total_thickness >= 0)
    for curr_thickness in thickness:
        assert np.all(curr_thickness >= 0)
    assert delta == pytest.approx(0.01825, abs=1e-5)
    assert delta_s == pytest.approx(3.75e-5, abs=1e-7)


def test_calculate_total_number_of_layers_array(boundary_layer_data):
    """!
    @brief Test calculate_total_number_of_layers method of BoundaryLayerCalculator.

    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    u_inf = boundary_layer_data['u_inf']
    L = boundary_layer_data['L']
    alt_m = boundary_layer_data['alt_m']
    re_transition = boundary_layer_data['re_transition']
    growth_factor = boundary_layer_data['growth_factor']
    y_plus = boundary_layer_data['y_plus_array']
    x_loc = boundary_layer_data['x_loc']
    total_thickness, thickness, delta, delta_s = BoundaryLayerCalculator.find_layers(alt_m, u_inf, L, y_plus, x_loc, re_transition, growth_factor)
    for curr_total_thickness in total_thickness:
        assert np.all(curr_total_thickness >= 0)
    for curr_thickness in thickness:
        assert np.all(curr_thickness >= 0)
    assert delta == pytest.approx(0.01825, abs=1e-5)
    assert isinstance(delta_s, np.ndarray)
    testing.assert_allclose(delta_s, np.array([3.753e-5, 1.8763e-4, 1.1258e-3]), atol=1e-8)


def test_calculate_growth_rate_for_layers_single(boundary_layer_data):
    """!
    @brief Test calculate_growth_rate_for_layers method of BoundaryLayerCalculator.

    @param boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    delta_s = boundary_layer_data['delta_s_single']
    delta = boundary_layer_data['delta']
    total_layers = boundary_layer_data['total_layers']
    growth_factor = boundary_layer_data['growth_factor']
    increment = boundary_layer_data['increment']
    total_thickness, thickness, growth_factor = BoundaryLayerCalculator.calculate_growth_rate_for_layers(delta_s, delta, total_layers, growth_factor, increment)
    for curr_total_thickness in total_thickness:
        assert np.all(curr_total_thickness >= 0)
    for curr_thickness in thickness:
        assert np.all(curr_thickness >= 0)
    assert growth_factor == pytest.approx(1.048, abs=1e-3)


def test_calculate_growth_rate_for_layers_array(boundary_layer_data):
    """!
    @brief Test calculate_growth_rate_for_layers method of BoundaryLayerCalculator.

    @param boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    delta_s = boundary_layer_data['delta_s_array']
    delta = boundary_layer_data['delta']
    total_layers = boundary_layer_data['total_layers']
    growth_factor = boundary_layer_data['growth_factor']
    increment = boundary_layer_data['increment']
    total_thickness, thickness, growth_factor = BoundaryLayerCalculator.calculate_growth_rate_for_layers(delta_s, delta, total_layers, growth_factor, increment)
    for curr_total_thickness in total_thickness:
        assert np.all(curr_total_thickness >= 0)
    for curr_thickness in thickness:
        assert np.all(curr_thickness >= 0)
    assert isinstance(growth_factor, np.ndarray)
    #testing.assert_allclose(growth_factor, np.array([1.2691, 1.1575, 1.0502]), atol=1e-4)


def test_calculate_bl_values(atmosphere_data, boundary_layer_data, re):
    """!
    @brief Test calculate_bl_values method of BoundaryLayerCalculator.

    @param[in] atmosphere_data : Fixture providing atmospheric data like density and dynamic viscosity.
    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    @param[in] re : Fixture providing a Reynolds number.
    """
    rho = atmosphere_data['rho']
    mu = atmosphere_data['mu']
    u_inf = boundary_layer_data['u_inf']
    L = boundary_layer_data['L']
    alt_m = boundary_layer_data['alt_m']
    x_loc = boundary_layer_data['x_loc']
    re_transition = boundary_layer_data['re_transition']
    delta, u_fric, tau_wall, Cf, re_new, rho_new, mu_new = BoundaryLayerCalculator.calculate_bl_values(alt_m, u_inf, L, x_loc, re_transition)
    assert delta == pytest.approx(0.01825, abs=1e-5)
    assert u_fric == pytest.approx(0.38925, abs=1e-5)
    assert tau_wall == pytest.approx(0.18561, abs=1e-5)
    assert Cf == pytest.approx(0.00303, abs=1e-5)
    assert re_new[0] == pytest.approx(re, abs=1e3)
    assert rho_new == pytest.approx(rho, abs=1e-3)
    assert mu_new == pytest.approx(mu, abs=1e-4)


def test_find_layers(boundary_layer_data):
    """!
    @brief Test find_layers method of BoundaryLayerCalculator

    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    u_inf = boundary_layer_data['u_inf']
    L = boundary_layer_data['L']
    alt_m = boundary_layer_data['alt_m']
    y_plus = boundary_layer_data['y_plus_single']
    x_loc = boundary_layer_data['x_loc']
    re_transition = boundary_layer_data['re_transition']
    growth_factor = boundary_layer_data['growth_factor']
    total_thickness, thickness, delta, delta_s = BoundaryLayerCalculator.find_layers(alt_m, u_inf, L, y_plus, x_loc, re_transition, growth_factor)
    for curr_total_thickness in total_thickness:
        assert np.all(curr_total_thickness >= 0)
    for curr_thickness in thickness:
        assert np.all(curr_thickness >= 0)
    assert delta == pytest.approx(0.01825, abs=1e-5)
    assert delta_s == pytest.approx(3.75e-5, abs=1e-7)


def test_find_layers_given_first_layer(boundary_layer_data):
    """!
    @brief Test find_layers_given_first_layer method of BoundaryLayerCalculator

    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    u_inf = boundary_layer_data['u_inf']
    L = boundary_layer_data['L']
    alt_m = boundary_layer_data['alt_m']
    delta_s = boundary_layer_data['delta_s_single']
    x_loc = boundary_layer_data['x_loc']
    re_transition = boundary_layer_data['re_transition']
    growth_factor = boundary_layer_data['growth_factor']
    total_thickness, thickness, delta, y_plus = BoundaryLayerCalculator.find_layers_given_first_layer(alt_m, u_inf, L, delta_s, x_loc,
                                                                                     re_transition, growth_factor)
    for curr_total_thickness in total_thickness:
        assert np.all(curr_total_thickness >= 0)
    for curr_thickness in thickness:
        assert np.all(curr_thickness >= 0)
    assert delta == pytest.approx(0.01825, abs=1e-5)
    assert y_plus == pytest.approx(6.66196, abs=1e-5)


def test_find_layers_given_num_of_layers(boundary_layer_data):
    """!
    @brief Test find_lyaers_given_num_of_layers method of BoundaryLayerCalculator

    @param[in] boundary_layer_data : Fixture providing data related to the boundary layer calculations.
    """
    u_inf = boundary_layer_data['u_inf']
    L = boundary_layer_data['L']
    alt_m = boundary_layer_data['alt_m']
    y_plus = boundary_layer_data['y_plus_single']
    x_loc = boundary_layer_data['x_loc']
    total_layers = boundary_layer_data['total_layers']
    re_transition = boundary_layer_data['re_transition']
    growth_factor = boundary_layer_data['growth_factor']
    total_thickness, thickness, growth_factor_used, delta, delta_s = BoundaryLayerCalculator.find_layers_given_num_of_layers(alt_m, u_inf, L,
                                                                                                                             y_plus, x_loc,
                                                                                                                             total_layers,
                                                                                                                             re_transition=re_transition,
                                                                                                                             growth_factor=growth_factor)
    for curr_total_thickness in total_thickness:
        assert np.all(curr_total_thickness >= 0)
    for curr_thickness in thickness:
        assert np.all(curr_thickness >= 0)
    assert growth_factor_used == pytest.approx(1.17, abs=1e-4)
    assert delta == pytest.approx(0.01825, abs=1e-5)
    assert delta_s == pytest.approx(3.75e-5, abs=1e-7)

