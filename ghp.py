import pandas as pd
import json

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
    
def ghp():
    """
    Function to calculate GHP (Master Production Schedule).

    Transforms data from JSON file, calculates planned production, and updates product availability information.
    """
    # Read data from the planned_orders.json file
    json_data = read_json_file('order.json')
    if json_data:
        df = pd.DataFrame(json_data["orders"])
        transposed_df = df.transpose()

    # Input storage data
    storage_data = read_json_file('product_details.json')

    # Input parameters responsible for GHP (Master Production Schedule)
    current_availability = storage_data["Deskorolka"]["initial_quantity"]
    lead_assemble_time = storage_data["Deskorolka"]["waiting_time_in_weeks"]

    # Update availability array
    availability_array = []
    planned_production_array = []

    for week in range(len(json_data['orders'])):
        week_data = json_data['orders'][week]
        week_number = week_data['week']
        demand = week_data['demand']
        planned_production = week_data['planned_production']
        availability_amount = week_data['availability']

        # If there is no planned demand
        if demand == 0:
            if planned_production == 0:
                planned_production_array.append(planned_production)
                if week_number == 1:
                    availability_array.append(current_availability)
                else:
                    availability_array.append(availability_array[week - 1])
            else:
                if week_number == 1:
                    planned_production_array.append(planned_production)
                    availability_array.append(current_availability + planned_production)
                else:
                    planned_production_array.append(planned_production)
                    availability_array.append(availability_array[week - 1] + planned_production)

        # If there is demand
        if demand > 0:
            if week_number == 1:
                if (current_availability < demand) and planned_production == 0:
                    planned_production = demand - current_availability
                planned_production_array.append(planned_production)
                availability_array.append(current_availability - demand + planned_production)
            else:
                if (availability_array[week-1] < demand) and planned_production == 0:
                    planned_production = demand - availability_array[week-1]
                planned_production_array.append(planned_production)
                availability_array.append(availability_array[week - 1] - demand + planned_production)
    
    # Update on-hand in the JSON data
    for week in range(len(json_data['orders'])):
        json_data['orders'][week]['availability'] = availability_array[week]
        json_data['orders'][week]['planned_production'] = planned_production_array[week]

    with open('planned_orders_ghp.json', 'w') as f:
        json.dump(json_data, f, indent=2)

    data_pd = read_json_file("planned_orders_ghp.json")
    data_pd_df = pd.DataFrame(data_pd["orders"])
    transposed_df = data_pd_df.transpose()
    print("Final GHP structure:")
    print(transposed_df.to_string(header=False))
    print("")
