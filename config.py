# Max workers that will run in parallel when making calls to the API
MAX_WORKERS = 8

# API key that is being passed on each call to an endpoint through the 'headers' dict
API_KEY = 'API_KEY'

# Headers are going to remain constant for all calls to various endpoints
HEADERS = {
    "API-AUTHENTICATION": API_KEY,
    "accept": "application/json",
    "content-type": "application/json"
}

# Required variables for the PATCH based on Revel API documentation. We need all of these per item
DESIRED_COLUMNS = [
    'combo_upcharge', 'id', 'establishment', 'name', 'attribute_type',
    'price', 'sorting', 'updated_by', 'variable_pricing_by',
    'tax_class', 'created_by', 'category'
]
