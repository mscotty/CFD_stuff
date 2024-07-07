import pytest
from unittest.mock import Mock

from CFD.mesh.FluidMechanicsCalculator import FluidMechanicsCalculator


@pytest.fixture
def fluid_calculator_inputs():
    """!
    @brief Define inputs utilized throughout the unit tests

    @param[out] fluid_calculator_inputs : dictionary with inputs required for the tests
    """
    return {
        'rho': 1.2,
        'mu': 0.01,
        'u_inf': 10,
        'L': 5,
        're': 5000,
        'Cf': 0.005,
        'delta_s': 0.01,
        'u_fric': 0.5
    }


def test_calculate_reynolds_number(fluid_calculator_inputs):
    """!
    @brief Test calculate_reynolds_number method of FluidMechanicsCalculator.

    @param[in] fluid_calculator_inputs : dictionary with inputs required for the tests
    """
    re = FluidMechanicsCalculator.calculate_reynolds_number(
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['mu'],
        fluid_calculator_inputs['u_inf'],
        fluid_calculator_inputs['L']
    )

    assert re == 6000.0


def test_calculate_friction_coefficient(fluid_calculator_inputs):
    """!
    @brief Test calculate_friction_coefficient method of FluidMechanicsCalculator.

    @param[in] fluid_calculator_inputs : dictionary with inputs required for the tests
    """
    re = FluidMechanicsCalculator.calculate_reynolds_number(
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['mu'],
        fluid_calculator_inputs['u_inf'],
        fluid_calculator_inputs['L']
    )

    Cf = FluidMechanicsCalculator.calculate_friction_coefficient(re)

    assert Cf == pytest.approx(0.0075, abs=1e-4)


def test_calculate_wall_shear(fluid_calculator_inputs):
    """!
    @brief Test calculate_wall_shear method of FluidMechanicsCalculator.

    @param[in] fluid_calculator_inputs : dictionary with inputs required for the tests
    """
    tau_wall = FluidMechanicsCalculator.calculate_wall_shear(
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['u_inf'],
        fluid_calculator_inputs['Cf']
    )

    assert tau_wall == 0.3


def test_calculate_fric(fluid_calculator_inputs):
    """!
    @brief Test calculate_fric method of FluidMechanicsCalculator.

    @param[in] fluid_calculator_inputs : dictionary with inputs required for the tests
    """
    re = FluidMechanicsCalculator.calculate_reynolds_number(
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['mu'],
        fluid_calculator_inputs['u_inf'],
        fluid_calculator_inputs['L']
    )

    Cf = FluidMechanicsCalculator.calculate_friction_coefficient(re)

    tau_wall = FluidMechanicsCalculator.calculate_wall_shear(
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['u_inf'],
        Cf
    )

    u_fric = FluidMechanicsCalculator.calculate_fric(
        fluid_calculator_inputs['rho'],
        tau_wall
    )

    assert u_fric == pytest.approx(0.6125, abs=1e-4)


def test_calculate_y_plus(fluid_calculator_inputs):
    """!
    @brief Test calculate_y_plus method of FluidMechanicsCalculator.

    @param[in] fluid_calculator_inputs : dictionary with inputs required for the tests
    """
    re = FluidMechanicsCalculator.calculate_reynolds_number(
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['mu'],
        fluid_calculator_inputs['u_inf'],
        fluid_calculator_inputs['L']
    )

    Cf = FluidMechanicsCalculator.calculate_friction_coefficient(re)

    tau_wall = FluidMechanicsCalculator.calculate_wall_shear(
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['u_inf'],
        Cf
    )

    fluid_calculator_inputs['u_fric'] = FluidMechanicsCalculator.calculate_fric(
        fluid_calculator_inputs['rho'],
        tau_wall
    )

    y_plus = FluidMechanicsCalculator.calculate_y_plus(
        fluid_calculator_inputs['delta_s'],
        fluid_calculator_inputs['u_fric'],
        fluid_calculator_inputs['rho'],
        fluid_calculator_inputs['mu']
    )

    assert y_plus == pytest.approx(0.7350, abs=1e-4)


