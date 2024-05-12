import json
import pandas as pd

def read_json_file(file_path):
    """
    Function to read data from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict or None: Content of the JSON file as a dictionary or None if the file is not found or does not contain valid JSON.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' does not contain valid JSON.")
        return None

def mrp(storageElementParentName, mrpObjectNameChild):
    """
    Function to perform Material Requirements Planning (MRP) calculations.

    Args:
        storageElementParentName (str): Name of the parent storage element.
        mrpObjectNameChild (str): Name of the child MRP object.

    Performs MRP calculations based on GHP data and updates MRP JSON files accordingly.
    """
    # Read GHP and MRP JSON files
    ghpObject = read_json_file('planned_orders_ghp.json')
    mrpObject = read_json_file('mrp_scheme.json')
    
    # Retrieve storage element data
    storageElementParent = read_json_file('product_details.json')[storageElementParentName]
    storageElementChild = read_json_file('product_details.json')[mrpObjectNameChild]

    # Extract relevant parameters
    waitingTimeInWeeks = storageElementParent["waiting_time_in_weeks"]
    currentLevel = storageElementChild['level']

    mrpOrders = mrpObject["orders"]

    # Calculate MRP based on GHP data for level 1 elements
    if currentLevel == 1:
        ghpOrders = ghpObject["orders"]
        for weekDataGhp in ghpOrders:
            if weekDataGhp["planned_production"] != 0:
                mrpIndex = weekDataGhp["week"] - waitingTimeInWeeks - 1
                mrpOrders[mrpIndex]["general_requirements"] = (int(weekDataGhp["planned_production"]) * int(storageElementChild['required_elements']))
    # Calculate MRP based on parent MRP data for level > 1 elements
    else:
        mrpParentOrders = read_json_file(storageElementParentName + '.json')

    fillOrder = True

    # Update MRP orders based on calculations
    weekDataMrpIndex = 0
    for weekDataMrp in mrpOrders:
        if weekDataMrp["general_requirements"] == 0 and fillOrder:
            mrpOrders[weekDataMrpIndex]["availability"] = storageElementChild["initial_quantity"]
        elif weekDataMrp["general_requirements"] == 0 and not fillOrder:
            weekDataMrp['availability'] = mrpOrders[weekDataMrpIndex - 1]['availability']
        elif fillOrder:
            fillOrder = False
            index = weekDataMrpIndex - storageElementChild['waiting_time_in_weeks']
            if mrpOrders[weekDataMrpIndex - 1]['availability'] <= weekDataMrp['general_requirements']:
                weekDataMrp['availability'] = mrpOrders[weekDataMrpIndex - 1]['availability'] - weekDataMrp['general_requirements']
                weekDataMrp['pure_need'] = weekDataMrp['general_requirements'] - mrpOrders[weekDataMrpIndex - 1]['availability']
            weekDataMrp['planned_receipts_orders'] = storageElementChild['units_per_batch']
            mrpOrders[index]['planned_release_orders'] = storageElementChild['units_per_batch']
            if index < 0:
                raise Exception("production is not available")
            weekDataMrp['availability'] = weekDataMrp['planned_receipts_orders'] + mrpOrders[weekDataMrpIndex - 1]['availability'] - weekDataMrp['general_requirements']
        elif weekDataMrp["general_requirements"] != 0 and not fillOrder:
            weekDataMrp['pure_need'] = weekDataMrp['general_requirements'] - mrpOrders[weekDataMrpIndex - 1]['availability']
            weekDataMrp['planned_receipts_orders'] = storageElementChild['units_per_batch']
            index = weekDataMrpIndex - storageElementChild['waiting_time_in_weeks']
            if index < 0:
                raise Exception("production is not available")
            mrpOrders[index]['planned_release_orders'] = storageElementChild['units_per_batch']
            weekDataMrp['availability'] = weekDataMrp['planned_receipts_orders'] + mrpOrders[weekDataMrpIndex - 1]['availability'] - weekDataMrp['general_requirements']
        
        weekDataMrpIndex += 1
    
    # Write updated MRP data to JSON file
    with open(mrpObjectNameChild + '.json', 'w') as f:
        json.dump(mrpOrders, f, indent=2)
    
    # Display MRP data
    pdMrpOrders = pd.DataFrame(mrpOrders)
    pdMrpOrders = pdMrpOrders.transpose()
    print("MRP Data:", mrpObjectNameChild)
    print(pdMrpOrders.to_string(header=False))
    print('Lead time', storageElementChild['waiting_time_in_weeks'], 'weeks')
    print('Lot size', storageElementChild['units_per_batch'], 'units per batch')
    print('Level', storageElementChild['level'], 'level')
    print('Initial quantity', storageElementChild['initial_quantity'], 'units')
    print("\n")
