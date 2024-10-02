import pandas as pd
from condition_check import check_if_item_needs_patch
from get_data import fetch_data_in_parallel
from patch_data import patch_product_data


''' This program is designed to go through the catering trays and locate discrepancies between the price of the 
    tray, and the default product upcharge amount. If those values are not equal, we need to patch the upcharge
    variable with the value of the price variable.
    
    This is necessary because the upcharge amount is not dynamic, so if the price of the tray is updated, this 
    variable would need to be manually updated to pull the new price. 
    
    3,048 items currently per establishment, with ~120 establishments and growing, requiring ~365,000 manual variable 
    updates without using this script.
    
    There are two different catering categories with items set up like this, one for online ordering, and the other
    being the traditional menu. There are a few items that this endpoint would return that we do not need to worry 
    about, so those items are filtered out of the data.
    
    All targeted establishments have the applicable items pulled and put into a dataframe. That dataframe is then
    filtered to find items where the condition check is false (price does not equal upcharge value). Those items are
    grouped in a separate dataframe, which is then passed along for patching.
    
    All items that are passed to the patch function are split into one of two groups; failed items or passed items. 
    This function generates two .csv files where the items can be examined after execution.'''

def main(data):
    # Get the product data for all selected establishments. ***Running against all est by default. Variable in config***
    all_product_data = fetch_data_in_parallel(data)

    # Converts the list of items into a dataframe
    df_products = pd.DataFrame(all_product_data)
    # Creating a csv file from the dataframe for logging purposes
    df_products.to_csv('data_files/products_data_.csv', index=False)

    # Running the dataframe through our condition check
    filtered_df = df_products[df_products.apply(check_if_item_needs_patch, axis=1)]
    # Creating a csv file from this filtered dataframe as well
    filtered_df.to_csv('data_files/products_data_filtered.csv', index=False)

    # Updates the items that failed the condition check
    print('\nPatching items:')
    patch_product_data(filtered_df)
