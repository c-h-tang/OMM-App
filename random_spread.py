import random

spread_bank = ['c', 'p', 'cs', 'cts', 'ps', 'pts', 
               'std', 'stg', 'cfly', 'ctfly', 
               'pfly', 'ptfly', 'ccon', 'pcon'
               ]
to_add = ['rr-c', 'rr-p', 'ifly', 'combo-c', 'combo-p', 'roll', 'cs1x2', 'ps1x2']

# number of strikes for spread
one_strike = ['c', 'p', 'cts', 'pts', 'std', 'ctfly', 'ptfly']
two_strike = ['cs', 'ps', 'stg', 'cfly', 'pfly']
four_strike = ['ccon', 'pcon']

# number of months for spread
one_month = ['c', 'p', 'cs', 'ps', 'std', 'stg', 'cfly', 'pfly', 'ccon', 'pcon']
two_month = ['cts', 'pts']
three_month = ['ctfly', 'ptfly']

strike_bank = [2000, 2100, 2200, 2300]
month_bank = ['N', 'Q', 'U', 'Z', 'H', 'M']
underlying_bank = [2400]

def generate_random_spread():
    spread = random.choice(spread_bank)
    underlying = random.choice(underlying_bank)
    strike_choice, strike_info = get_strikes(spread)
    month_choice, month_info = get_months(spread)
    spread_to_price = f"Tied to {underlying}, {month_choice} {strike_choice} {spread}"
    return spread_to_price, (underlying, spread, month_info, strike_info)

    
def get_months(spread):
    months = []
    if spread in one_month:
        selection = random.choice(month_bank)
        return selection, selection
    elif spread in two_month:
        months = random.sample(month_bank, 2)
    elif spread in three_month:
        months = random.sample(month_bank, 3)
    else:
        return "Month selection error"
    months.sort()
    months_string  = ' '.join(str(ele) for ele in months)
    return months_string, months
    
def get_strikes(spread):
    strikes = []
    if spread in one_strike:
        selection = random.choice(strike_bank)
        return selection, selection
    elif spread in two_strike:
        strikes = random.sample(strike_bank, 2)
    elif spread in four_strike:
        strikes = random.sample(strike_bank, 4)
    else:
        return "Strike selection error"
    strikes.sort()
    strikes_string  = ' '.join(str(ele) for ele in strikes)
    return strikes_string, strikes

