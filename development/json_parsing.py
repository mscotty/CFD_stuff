import json
from typing import Union, List, Dict, Any


def explore_json(json_data: Any, prefix: str = "") -> None:
    """
    Explore the structure of JSON data.

    Parameters:
    - json_data (Any): JSON data to explore.
    - prefix (str): Prefix for displaying the structure.

    Returns:
    - None
    """
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            explore_json(value, new_prefix)
    elif isinstance(json_data, list):
        for i, value in enumerate(json_data):
            new_prefix = f"{prefix}[{i}]"
            explore_json(value, new_prefix)
    else:
        print(f"{prefix}: {json_data}")


def process_sizing(sizing_data: Dict[str, Dict[str, Union[int, float]]]) -> None:
    """
    Process sizing data by multiplying values based on field names.

    Parameters:
    - sizing_data (Dict[str, Dict[str, Union[int, float]]]): Sizing data to be processed.

    Returns:
    - None
    """
    for category_name, category_data in sizing_data.items():
        for field_name, field_value in category_data.items():
            # Multiply values by 2 or 3 based on the field name
            if field_name.startswith("param"):
                category_data[field_name] *= 2
            else:
                category_data[field_name] *= 3


def process_global_sizing(sizing_data: Dict[str, Union[int, float]]) -> Dict[str, Union[int, float]]:
    """
    Process global sizing data by multiplying values based on field names.

    Parameters:
    - sizing_data (Dict[str, Union[int, float]]): Global sizing data to be processed.

    Returns:
    - Dict[str, Union[int, float]]: Processed global sizing data.
    """
    processed_data = {}
    for field_name, field_value in sizing_data.items():
        if field_name == "param1":
            processed_data[field_name] = field_value * 2
        elif field_name == "param2":
            processed_data[field_name] = field_value * 3
        elif field_name == "param3":
            processed_data[field_name] = field_value * 4
        else:
            processed_data[field_name] = field_value
    return processed_data


def process_topo_sizing(sizing_data: Dict[str, Union[int, float]]) -> Dict[str, Union[int, float]]:
    """
    Process topo sizing data by multiplying values based on field names.

    Parameters:
    - sizing_data (Dict[str, Union[int, float]]): Topo sizing data to be processed.

    Returns:
    - Dict[str, Union[int, float]]: Processed topo sizing data.
    """
    processed_data = {}
    for field_name, field_value in sizing_data.items():
        if field_name == "param1":
            processed_data[field_name] = field_value * 2
        elif field_name == "param2":
            processed_data[field_name] = field_value * 3
        elif field_name == "param3":
            processed_data[field_name] = field_value * 4
        else:
            processed_data[field_name] = field_value
    return processed_data


def process_bl_sizing(sizing_data: Dict[str, Union[int, float]]) -> Dict[str, Union[int, float]]:
    """
    Process BL sizing data by multiplying values by 2.

    Parameters:
    - sizing_data (Dict[str, Union[int, float]]): BL sizing data to be processed.

    Returns:
    - Dict[str, Union[int, float]]: Processed BL sizing data.
    """
    processed_data = {}
    for field_name, field_value in sizing_data.items():
        processed_data[field_name] = field_value * 2

    return processed_data


if __name__ == '__main__':
    json_file = 'D:/Mitchell/Work/civilian/CFD/example.json'

    # Parse JSON file
    with open(json_file, 'r') as fid:
        data = json.load(fid)

    # Convert BL_Sizing lists to dictionaries
    for key, value in data.items():
        if "BL_Sizing" in value:
            data[key]["BL_Sizing"] = dict(zip(value["BL_Sizing"]["name"], value["BL_Sizing"]["val"]))

    # Loop through the top-level keys ("body", "wing")
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
                            value[key2] = process_global_sizing(sizing_data)
                        elif key2 == "Topo_Sizing":
                            # execute other sizing changes
                            value[key2] = process_topo_sizing(sizing_data)
                        elif key2 == "BL_Sizing":
                            # execute BL sizing changes
                            value[key2] = process_bl_sizing(sizing_data)
                        else:
                            print("Not Supported Keyword")

                        print("\nUpdated Sizing:")
                        print(json.dumps({"Sizing": value[key2]}, indent=2))
                    else:
                        print(f"Invalid Sizing information found for {key2}")
                else:
                    print(f"No Sizing information found for {key}")

    # Print the final updated data
    print("\nFinal Updated Data:")
    print(json.dumps(data, indent=2))
