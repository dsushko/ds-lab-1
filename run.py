import operator
import os
import re
import numpy as np

from flask import Flask, render_template, request, url_for, request, redirect, abort
from mpmath import mp

mp.prec = 250
mp.dps = 25

ops_mapping = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-result', methods=['GET', 'POST'])
def get_result():
    s = ''
    args = dict(request.form)
    print(args)
    try:
        nums = [args[f'num{i}'] for i in range(1, 5)]
        ops = [args[f'op{i}'] for i in range(1, 4)]
        for num in nums:
            validate_input(num)

        for ind, num in enumerate(nums):
            nums[ind] = preprocess_input(num)
        print(nums)
        res = calculate(
            num1=nums[0],
            num2=nums[1],
            num3=nums[2],
            num4=nums[3],
            op1=ops[0],
            op2=ops[1],
            op3=ops[2]
        )
        res = postprocess_output(res)
        round_res = str(myround(res.replace(' ', ''), type=args['round-type']))
    except ZeroDivisionError as e:
        return render_template('index.html', res='На ноль делить нельзя')
    except Exception as e:
        return render_template('index.html', res=str(e))
    return render_template('index.html', res=res, round_res=round_res)

def validate_input(s):
    valid_num_regex = re.compile("([+-]?[1-9][0-9]{0,2}(( [0-9]{3})*)([.,][0-9]*)?)|([+-]?[1-9][0-9]*([.,][0-9]*)?)|([+-]?0([.,][0-9]*)?)")
    if not valid_num_regex.fullmatch(s):
        raise Exception(f'{s} - Число неправильного формата')
    print(f'{s} passed')

def preprocess_input(s):
    s = s.replace('.', ',').replace(',', '.').replace(' ', '')
    return mp.mpf(s)

def mpfround(n, prec=10):
    wholepart, fracpart = str(n).split(".")
    fracpart = str(np.around(float(f'.{fracpart}'), prec))
    return mp.mpf(wholepart + '.' + str(fracpart).split('.')[1])

def calculate(num1, num2, num3, num4, op1, op2, op3):
    parenthesis_res = ops_mapping[op2](num2, num3)
    print(parenthesis_res)
    if op3 in ['*', '/'] and op1 in ['+', '-']:
        res = mpfround(ops_mapping[op3](parenthesis_res, num4), 6 if op3 == '/' else 10)
        res = mpfround(ops_mapping[op1](num1, res), 6 if op1 == '/' else 10)
    else:
        res = mpfround(ops_mapping[op3](num1, parenthesis_res), 6 if op3 == '/' else 10)
        res = mpfround(ops_mapping[op1](res, num4), 6 if op1 == '/' else 10)
    return res

def postprocess_output(s):
    s = str(s)
    wpart, fpart = s.split('.')
    fpart = fpart[:6]

    wpart_new = []
    i = 1
    for c in wpart[::-1]:
        wpart_new.append(c)
        if i % 3 == 0:
            wpart_new.append(' ')
            i -= 3
        i += 1
    wpart = ''.join(wpart_new[::-1])

    s = f'{wpart}.{fpart}'
    s = s.rstrip('0')
    if s[-1] == '.':
        s = s + '0'
    return s

def myround(s, type):
    w, f = s.split('.')
    f = '.' + f
    w = int(w)
    if type == 'math':
        f = np.round_(float(f))
    if type == 'gauss':
        f = np.around(float(f))
    if type == 'cutoff':
        return s.split('.')[0]
    if f == 1:
        w += 1
    
    wpart_new = []
    i = 1
    for c in str(w)[::-1]:
        wpart_new.append(c)
        if i % 3 == 0:
            wpart_new.append(' ')
            i -= 3
        i += 1

    return ''.join(wpart_new[::-1])


if os.environ.get('APP_LOCATION') == 'heroku':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
else:
    app.run(host='localhost', port=8080, debug=True)