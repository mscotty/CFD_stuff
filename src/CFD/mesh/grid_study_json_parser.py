import json
from typing import Union, List, Dict, Any
from copy import deepcopy

from CFD.utilities.atmosphere import AtmosphereModel
from CFD.mesh.BoundaryLayerCalculator import BoundaryLayerCalculator


def read_flight_conditions_json(json_file):
    with open(json_file, 'r') as fid:
        data = json.load(fid)
    if 'alt' in data:
        atm = AtmosphereModel(data['alt'])
    if 'rho' not in data:
        # Not supporting arrays at this time
        data['rho'] = atm.density[0]
    if 'mu' not in data:
        # Not supporting arrays at this time
        data['mu'] = atm.dynamic_viscosity[0]
    return data


def process_global_sizing(sizing_data: Dict[str, Union[int, float]], 
                          grid_factor: float) -> Dict[str, Union[int, float]]:
    """
    Process global sizing data by multiplying values based on field names.

    Parameters:
    - sizing_data (Dict[str, Union[int, float]]): Global sizing data to be processed.
    - grid_factor (float): Grid factor to scale sizing data.

    Returns:
    - Dict[str, Union[int, float]]: Processed global sizing data.
    """
    processed_data = {}
    for field_name, field_value in sizing_data.items():
        if field_name == "Scaling_Factor":
            processed_data[field_name] = field_value * grid_factor
        elif field_name == "Global_Size":
            processed_data[field_name] = field_value * grid_factor
        elif field_name == "Minimum_Size":
            processed_data[field_name] = field_value * grid_factor
        elif field_name == "Size_Increment":
            processed_data[field_name] = 1 + (field_value-1) * grid_factor
        else:
            processed_data[field_name] = field_value
    return processed_data


def process_topo_sizing(sizing_data: Dict[str, Union[int, float]], 
                        grid_factor: float) -> Dict[str, Union[int, float]]:
    """
    Process topo sizing data by multiplying values based on field names.

    Parameters:
    - sizing_data (Dict[str, Union[int, float]]): Topo sizing data to be processed.
    - grid_factor (float): Grid factor to scale sizing data.

    Returns:
    - Dict[str, Union[int, float]]: Processed topo sizing data.
    """
    processed_data = {}
    for field_name, field_value in sizing_data.items():
        processed_data[field_name] = field_value * grid_factor
    return processed_data


def process_bl_sizing(sizing_data: Dict[str, Union[int, float]], 
                      flight_data, 
                      grid_factor: float) -> Dict[str, Union[int, float]]:
    """
    Process BL sizing data by multiplying values.

    Parameters:
    - sizing_data (Dict[str, Union[int, float]]): BL sizing data to be processed.
    - grid_factor (float): Grid factor to scale sizing data.

    Returns:
    - Dict[str, Union[int, float]]: Processed BL sizing data.
    """
    processed_data = {}
    for field_name, field_value in sizing_data.items():
        processed_data[field_name] = {}
        _, _, growth_factor, _, _ = BoundaryLayerCalculator.find_layers_given_num_of_layers(flight_data['alt'], 
                                                                                            flight_data['u_inf'], 
                                                                                            flight_data['L'], 
                                                                                            flight_data['y_plus'],
                                                                                            flight_data['L'],
                                                                                            flight_data['num_of_layers'],
                                                                                            field_value['1st_Layer_Thickness'] * grid_factor)
        for field_name2, field_value2 in field_value.items():
            if field_name2 == "Growth_Rate":
                processed_data[field_name][field_name2] = growth_factor[0]
            elif field_name2 == "1st_Layer_Thickness":
                processed_data[field_name][field_name2] = field_value2 * grid_factor
            elif field_name2 == "Number_of_Layers":
                processed_data[field_name][field_name2] = field_value2
            else:
                processed_data[field_name][field_name2] = field_value2

    return processed_data


def load_and_reformat_json(json_file: str) -> Dict[str, Any]:
    """
    Load and reformat JSON data.

    Parameters:
    - json_file (str): Path to the JSON file.

    Returns:
    - Dict[str, Any]: Reformatted JSON data.
    """
    # Parse JSON file
    with open(json_file, 'r') as fid:
        data = json.load(fid)

    # Convert BL_Sizing lists to dictionaries
    for key, value in data.items():
        for key2, value2 in value.items():
            if "Topo_Sizing" == key2:
                data[key]["Topo_Sizing"] = dict(zip(value2["name"], value2["val"]))
            elif "BL_Sizing" == key2:
                bl_sizing_data = {}
                for name, growth_rate, thickness, layers in zip(
                        value2["name"],
                        value2["Growth_Rate"],
                        value2["1st_Layer_Thickness"],
                        value2["Number_of_Layers"]
                ):
                    bl_sizing_data[name] = {"Growth_Rate": growth_rate,
                                            "1st_Layer_Thickness": thickness,
                                            "Number_of_Layers": layers}

                # Update the original data with the new BL_Sizing structure
                data[key]["BL_Sizing"] = bl_sizing_data
    return data


def write_new_mesh_json(data, json_filename):
    with open(json_filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def update_mesh_grid_values(data: Dict[str, Any], flight_data, grid_factors: List[float], grid_json_file="grid.json") -> Dict[str, Any]:
    """
    Update mesh grid values.

    Parameters:
    - data (Dict[str, Any]): Original data.
    - grid_factors (List[float]): List of grid factors to apply.

    Returns:
    - Dict[str, Any]: Updated data.
    """
    out_json_parts = grid_json_file.split('.')
    grids = {}
    for grid_factor in grid_factors:
        # Loop through the top-level keys ("body", "wing")
        print("Grid Factor: " + str(grid_factor))
        new_data = deepcopy(data)
        for key, value in data.items():
            print(f"\nProcessing {key}:")
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    # Check if "Sizing" is in the key
                    if "Sizing" in key2:
                        sizing_data = value2

                        # Check if it's a dictionary with expected keys
                        if isinstance(sizing_data, dict):
                            # Loop through the Sizing information
                            print("\nOriginal Sizing:")
                            print(json.dumps(sizing_data, indent=2))

                            # Add in logic for sizing
                            if key2 == "Global_Sizing":
                                # execute global sizing changes
                                new_data[key][key2] = process_global_sizing(sizing_data, grid_factor)
                            elif key2 == "Topo_Sizing":
                                # execute other sizing changes
                                new_data[key][key2] = process_topo_sizing(sizing_data, grid_factor)
                            elif key2 == "BL_Sizing":
                                # execute BL sizing changes
                                new_data[key][key2] = process_bl_sizing(sizing_data, flight_data, grid_factor)
                            else:
                                print("Not Supported Keyword")

                            print("\nUpdated Sizing:")
                            print(json.dumps(new_data[key][key2], indent=2))  # Change here
                            print("\n")
                        else:
                            print(f"Invalid Sizing information found for {key2}")
                    else:
                        print(f"No Sizing information found for {key}")
            write_new_mesh_json(new_data, out_json_parts[0] + str(grid_factor) + '.' + out_json_parts[1])
            grids["factor" + str(grid_factor)] = new_data

    # Print the final updated data
    write_new_mesh_json(grids, out_json_parts[0] + "_complete." + out_json_parts[1])
    print("\nFinal Updated Data:")
    print(json.dumps(grids, indent=2))
    return data


def create_new_grids(grid_json_file: str, flight_json_file: str, grid_factors: List[float]) -> None:
    """
    Create new grids based on JSON file and grid factors.

    Parameters:
    - json_file (str): Path to the JSON file.
    - grid_factors (List[float]): List of grid factors to apply.
    """
    print('starting')
    flight_data = read_flight_conditions_json(flight_json_file)
    print('read flight json')
    data = load_and_reformat_json(grid_json_file)
    print('read grid json')
    data = update_mesh_grid_values(data, flight_data, grid_factors, grid_json_file)
    # add in code to handle API for Capstone with data


if __name__ == '__main__':
    # change
    grid_json_file = "C:/Users/1549059747C/OneDrive - United States Air Force/Documents/Work/python/cfd_code/example_grid.json"
    flight_json_file = "C:/Users/1549059747C/OneDrive - United States Air Force/Documents/Work/python/cfd_code/example_flight.json"

    create_new_grids(grid_json_file, flight_json_file, [0.75, 1.0, 1.5, 2.0])
