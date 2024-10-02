# Condition check to see if 'price' does not equal 'combo_upcharge'
def check_if_item_needs_patch(row):
    try:
        price = float(row['price'])
        combo_upcharge = float(row['combo_upcharge'])
        return price != combo_upcharge
    except ValueError:
        return False
    