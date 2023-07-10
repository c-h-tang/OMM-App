from flask import Flask, jsonify, render_template, request, current_app, send_file
import pandas as pd
from random_spread import generate_random_spread
import numpy as np
from scipy.spatial import KDTree

app = Flask(__name__)

# change as necessary
df = None
numCorrect = 0
selected_spread = None
selected_spread_info = None
   
def generate_outright_theo(underlying, spread_type, strike, month):
    return round(df.loc[(df['Underlying'] == underlying) & (df['Type'] == spread_type) & (df['Strike'] == strike) & (df['Month'] == month), 'TV'].values[0], 2)

def generate_butterfly_theo(underlying, spread_type, low_strike, high_strike, month):
    lower = generate_outright_theo(underlying, spread_type, low_strike, month)
    mid = generate_outright_theo(underlying, spread_type, (high_strike + low_strike) / 2, month)
    upper = generate_outright_theo(underlying, spread_type, high_strike, month)
    return round((upper - mid) - (mid - lower), 2) if spread_type == 'Put' else round((lower - mid) - (mid - upper), 2)

def generate_straddle_theo(underlying, strike, month):
    call_theo = generate_outright_theo(underlying, 'Call', strike, month)
    put_theo = generate_outright_theo(underlying, 'Put', strike, month)
    return round(call_theo + put_theo, 2)

def generate_strangle_theo(underlying, low_strike, high_strike, month, guts):
    if guts:
        return round(generate_outright_theo(underlying, 'Call', high_strike, month) + generate_outright_theo(underlying, 'Put', low_strike, month), 2)
    return round(generate_outright_theo(underlying, 'Call', low_strike, month) + generate_outright_theo(underlying, 'Put', high_strike, month), 2)


def generate_call_put_spread_theo(underlying, spread_type, low_strike, high_strike, month):
    if spread_type == 'Put':
        return round(generate_outright_theo(underlying, spread_type, high_strike, month) - generate_outright_theo(underlying, spread_type, low_strike, month), 2)
    return round(generate_outright_theo(underlying, spread_type, low_strike, month) - generate_outright_theo(underlying, spread_type, high_strike, month), 2)

def generate_call_put_time_spread_theo(underlying, spread_type, strike, close_month, far_month):
    return round(generate_outright_theo(underlying, spread_type, strike, far_month) - generate_outright_theo(underlying, spread_type, strike, close_month), 2)

def generate_condor_theo(underlying, spread_type, low_strike, mid_low_strike, mid_high_strike, high_strike, month):
    wings = generate_outright_theo(underlying, spread_type, low_strike, month) + generate_outright_theo(underlying, spread_type, high_strike, month)
    guts = generate_outright_theo(underlying, spread_type, mid_low_strike, month) + generate_outright_theo(underlying, spread_type, mid_high_strike, month)
    return round(wings - guts, 2) if spread_type == 'Call' else round(guts - wings, 2)

def generate_timefly_theo(underlying, spread_type, strike, close_month, mid_month, far_month, guts_bool):
    wings = generate_outright_theo(underlying, spread_type, strike, close_month) + generate_outright_theo(underlying, spread_type, strike, far_month)
    guts = 2 * generate_outright_theo(underlying, spread_type, strike, mid_month)
    return round(guts - wings, 2) if guts_bool else round(wings - guts, 2)


def expected_theo(spread):
    print(spread)
    spread_underlying = spread[0]
    spread_name = spread[1]
    spread_month = spread[2]
    spread_strike = spread[3]

    if spread_name == 'c':
        return generate_outright_theo(spread_underlying, 'Call', spread_strike, spread_month)
    elif spread_name == 'p':
        return generate_outright_theo(spread_underlying, 'Put', spread_strike, spread_month)
    elif spread_name == 'cs':
        return generate_call_put_spread_theo(spread_underlying, 'Call', spread_strike[0], spread_strike[1], spread_month)
    elif spread_name == 'ps':
        return generate_call_put_spread_theo(spread_underlying, 'Put', spread_strike[0], spread_strike[1], spread_month)
    elif spread_name == 'cts':
        return generate_call_put_time_spread_theo(spread_underlying, 'Call', spread_strike, spread_month[0], spread_month[1])
    elif spread_name == 'pts':
        return generate_call_put_time_spread_theo(spread_underlying, 'Put', spread_strike, spread_month[0], spread_month[1])
    elif spread_name == 'std':
        return generate_straddle_theo(spread_underlying, spread_strike, spread_month)
    elif spread_name == 'stg': # assuming no gut strangle?
        return generate_strangle_theo(spread_underlying, spread_strike[0], spread_strike[1], spread_month, True)
    elif spread_name == 'cfly':
        # TODO: add logic to make it so that the guts and wings are valid strike prices
        return generate_butterfly_theo(spread_underlying, 'Call', 2000, 2200, spread_month)
    elif spread_name == 'pfly':
        return generate_butterfly_theo(spread_underlying, 'Put', 2000, 2200, spread_month)
    elif spread_name == 'ctfly': # assuming no guts tfly
        return generate_timefly_theo(spread_underlying, 'Call', spread_strike, spread_month[0], spread_month[1], spread_month[2], False)
    elif spread_name == 'ptfly': # assuming no guts tfly
        return generate_timefly_theo(spread_underlying, 'Put', spread_strike, spread_month[0], spread_month[1], spread_month[2], False)
    elif spread_name == 'ccon':
        return generate_condor_theo(spread_underlying, 'Call', spread_strike[0], spread_strike[1], spread_strike[2], spread_strike[3], spread_month)
    elif spread_name == 'pcon':
        return generate_condor_theo(spread_underlying, 'Put', spread_strike[0], spread_strike[1], spread_strike[2], spread_strike[3], spread_month)
    return 0

@app.route('/', methods=['GET', 'POST'])
def home():
  global numCorrect
  global selected_spread
  global selected_spread_info

  if request.method == 'POST':
    print("POST")
    try:
        answer = float(request.form['answer'])
    except ValueError:
        return render_template("index.html", random_spread=selected_spread, invalid=True)
    expected = expected_theo(selected_spread_info)
    print('answer = ', answer, '    vs.      expected = ', expected)
    if answer == expected:
        numCorrect += 1
    print("numCorrect = ", numCorrect)
    selected_spread, selected_spread_info = generate_random_spread()
    return render_template("index.html", random_spread=selected_spread, expected=expected, answer=answer, invalid=False)
  else:
    print("GET")
    selected_spread, selected_spread_info = generate_random_spread()
    return render_template("index.html", random_spread=selected_spread)

def test():
    theo = generate_butterfly_theo(2400, 'Call', 2000, 2200, 'U')
    print("2000 2200 c-fly TV = ", theo)
    theo2 = generate_outright_theo(2400, 'Put', 2200, 'U')
    print("2200 p TV = ", theo2)
    theo3 = generate_strangle_theo(2400, 2000, 2100, 'U', True)
    print("2000 2100 gut stg = ", theo3)
    theo4 = generate_straddle_theo(2400, 2200, 'U')
    print("2200 std TV = ", theo4)
    theo5 = generate_call_put_spread_theo(2400, 'Call', 2000, 2200, 'U')
    print("2000 2200 cs TV = ", theo5)
    theo6 = generate_call_put_spread_theo(2400, 'Put', 2000, 2200, 'U')
    print("2000 2200 ps TV = ", theo6)

@app.before_first_request
def initiate():
    global df

    excel_file_path = 'TestTV - Copy.xlsx'
    df = pd.read_excel(excel_file_path)
    print(df)

    #test()