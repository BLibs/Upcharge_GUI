import pandas as pd
import requests
from config import HEADERS


# Takes the full dataset that we filtered for condition check after populating from process_establishment_data func
def patch_product_data(filtered_df):
    # Creating lists and counter for failed items and passed items
    non_202_data = []
    success_202_data = []
    failed_count = 0
    passed_count = 0

    # Iterate over each row in the filtered dataframe
    for index, row in filtered_df.iterrows():
        # Get the product id that will be appended to the URL
        product_id = str(row['id'])
        # Prepare the data for the item that is going to be patched, passed in json through patch request
        data = {
            "name": row['name'],
            "price": float(row['price']),
            "establishment": row['establishment'],
            "updated_by": row['updated_by'],
            "created_by": row['created_by'],
            "category": row['category'],
            "attribute_type": int(row['attribute_type']),
            "tax_class": int(row['tax_class']),
            "variable_pricing_by": int(row['variable_pricing_by']),
            "sorting": int(row['sorting']),
            "combo_upcharge": str(float(row['price']))
        }
        # Passing product id to the endpoint
        url = f'https://primohoagies.revelup.com/resources/Product/{product_id}/'
        # Passing the json data on the patch request
        response = requests.patch(url, headers=HEADERS, json=data)

        # Check the status code of the response. 202 would be successful
        if response.status_code != 202:
            # Increment the failed variable
            failed_count += 1
            # Save the details of the non-202 response to the list
            non_202_data.append({
                'product_id': product_id,
                'name': row['name'],
                'establishment': row['establishment'],
                'category': row['category'],
                'status_code': response.status_code,
                'response_text': response.text
            })

        else:
            # Increment the total of passed items
            passed_count += 1
            # Save the details of the 202 response to the list
            success_202_data.append({
                'product_id': product_id,
                'name': row['name'],
                'establishment': row['establishment'],
                'status_code': response.status_code,
                'response_text': response.text
            })

        # Printing updates on each item as they are patched
        print(f'Updated product {row["name"]} with ID {product_id}, Status Code: {response.status_code}')

    # Convert the list of dictionaries to a DataFrame
    df_non_202_responses = pd.DataFrame(non_202_data)
    df_202_responses = pd.DataFrame(success_202_data)

    # Saving the passed and failed items to a csv file
    df_non_202_responses.to_csv('data_files/failed_items.csv', index=False)
    df_202_responses.to_csv('data_files/passed_items.csv', index=False)

    # Print the number of failed items and the number of passed items
    print(failed_count, 'items failed to update. See the failed_items.csv for more information.')
    print(passed_count, 'items were patched successfully. See the passed_items.csv file for more information')
