"""
@brief Unit tests for grid_study_json_parser module.

@file test_grid_study_json_parser.py
"""

import os
import math
import unittest
import json
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any
from copy import deepcopy

import pytest
import numpy as np
from numpy import testing

from CFD.mesh.grid_study_json_parser import *

@pytest.fixture
def flight_json():
    """
    Fixture for flight JSON file.
    """
    return os.path.dirname(__file__) + "/example_flight_test.json"


@pytest.fixture
def grid_json():
    """
    Fixture for grid JSON file.
    """
    return os.path.dirname(__file__) + "/example_grid_test.json"


def test_read_flight_conditions_json(flight_json):
    """
    Test for read_flight_conditions_json function.
    """
    data = read_flight_conditions_json(flight_json)
    assert isinstance(data, dict)


def test_read_flight_conditions_json_mock():
    """
    Test for read_flight_conditions_json function with mocking.
    """
    with patch("builtins.open", MagicMock()) as mock_open:
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = '{"alt": 100}'
        mock_open.return_value = mock_file
        data = read_flight_conditions_json("test.json")
        expected_data = {"alt": 100, "mu": 1.78624e-5, "rho": 1.213283}
        assert all(math.isclose(data.get(key), value, rel_tol=1e-5) for key, value in expected_data.items()), \
            "Values do not match within tolerance"


def test_process_global_sizing():
    """
    Test for process_global_sizing function.
    """
    sizing_data = {"Scaling_Factor": 2, "Global_Size": 10}
    processed_data = process_global_sizing(sizing_data, 1.5)
    assert processed_data == {"Scaling_Factor": 3, "Global_Size": 15}


def test_process_topo_sizing():
    """
    Test for process_topo_sizing function.
    """
    sizing_data = {"Size1": 10, "Size2": 20}
    processed_data = process_topo_sizing(sizing_data, 0.5)
    assert processed_data == {"Size1": 5, "Size2": 10}


def test_process_bl_sizing():
    """
    Test for process_bl_sizing function.
    """
    sizing_data = {"Layer1": {"Growth_Rate": 1, "1st_Layer_Thickness": 0.1, "Number_of_Layers": 5}}
    flight_data = {'alt': 100, 'u_inf': 10, 'L': 50, 'y_plus': 1, 'num_of_layers': 5}
    processed_data = process_bl_sizing(sizing_data, flight_data, 2)
    expected_data = {"Layer1": {"Growth_Rate": 0.929, "1st_Layer_Thickness": 0.2, "Number_of_Layers": 5}}
    assert round(processed_data["Layer1"]["Growth_Rate"], 5) == expected_data["Layer1"]["Growth_Rate"]


def test_load_and_reformat_json(grid_json):
    """
    Test for load_and_reformat_json function.
    """
    # JSON data embedded as a string
    json_data = '''
        {
            "body": {
                "Global_Sizing": {
                    "Scaling_Factor": 1.0,
                    "Global_Size": 1.0,
                    "Minimum_Size": 1e-05,
                    "Size_Increment": 1.2
                },
                "Topo_Sizing": {
                    "FrontNose": 0.02,
                    "Nose": 0.035,
                    "Body": 0.05,
                    "BackEnd": 0.15
                },
                "BL_Sizing": {
                    "Face B.L.": {
                        "Growth_Rate": 1.2,
                        "1st_Layer_Thickness": 3e-05,
                        "Number_of_Layers": 31
                    },
                    "Edge B.L.": {
                        "Growth_Rate": 1.3,
                        "1st_Layer_Thickness": 5e-05,
                        "Number_of_Layers": 30
                    }
                }
            },
            "wing": {
                "Global_Sizing": {
                    "Scaling_Factor": 1.0,
                    "Global_Size": 1.0,
                    "Minimum_Size": 1e-05,
                    "Size_Increment": 1.2
                },
                "Topo_Sizing": {
                    "WingEdge": 0.01,
                    "WingTopBottom": 0.01
                },
                "BL_Sizing": {
                    "Face B.L.": {
                        "Growth_Rate": 1.2,
                        "1st_Layer_Thickness": 3e-05,
                        "Number_of_Layers": 30
                    }
                }
            }
        }
        '''

    # Convert the JSON string to a Python dictionary
    expected_data = json.loads(json_data)
    data = load_and_reformat_json(grid_json)
    assert data == expected_data


def test_update_mesh_grid_values():
    """
    Test for update_mesh_grid_values function.
    """
    data = {"body": {"Global_Sizing": {"Size1": 10}}, "wing": {"Topo_Sizing": {"Size2": 20}}}
    flight_data = {'alt': 100, 'u_inf': 10, 'L': 50, 'y_plus': 1, 'num_of_layers': 5}
    updated_data = update_mesh_grid_values(data, flight_data, [1.0])
    assert updated_data == data


def test_create_new_grids():
    """
    Test for create_new_grids function.
    """
    with patch("CFD.mesh.grid_study_json_parser.read_flight_conditions_json") as mock_read_flight:
        with patch("CFD.mesh.grid_study_json_parser.load_and_reformat_json") as mock_load_reformat:
            with patch("CFD.mesh.grid_study_json_parser.update_mesh_grid_values") as mock_update_grid:
                create_new_grids("grid.json", "flight.json", [1.0])
                mock_read_flight.assert_called_once_with("flight.json")
                mock_load_reformat.assert_called_once_with("grid.json")
                mock_update_grid.assert_called_once()

