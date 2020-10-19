from flask import Flask
from flask_socketio import SocketIO, send
from flask import render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'calappsecret_key'
socketio = SocketIO(app, cors_allowed_origins='*')

import operator

DIGITS = set('0123456789')
OPERATIONS = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.floordiv,
    '^' : operator.pow,
}


def is_digit(var):
    return var in DIGITS

def get_number(varstr):
    s = ""
    for c in varstr:
        if not is_digit(c):
            break
        s += c
    return (int(s), len(s))

def perform_operation(string, num1, num2):
    op = OPERATIONS.get(string, None)
    if op is not None:
        return op(num1, num2)
    else:
        return None  # How to handle this?

def eval_math_expr(expr):
    negate = False
    while True:
        try:
            if expr[0] == '-': #for negative numbers
                negate = True #because here the numbers are string format
                expr = expr[1:]
            number1, end_number1 = get_number(expr)
            expr = expr[end_number1:]
            if negate == True:
                number1 = -number1
                negate = False
            if expr == '':
                return number1
            op = expr[0]
            expr = expr[1:]
            number2, end_number2 = get_number(expr)
            result = perform_operation(op, number1, number2)
            number1 = result
            expr = str(number1) + expr[end_number2:]
        except Exception as e:
            print(e)
            break
    return number1

queue=[]
@socketio.on('message')
def handleMessage(msg):
    if msg != 'User has connected!':
        queue.append(msg + ' = ' + str(eval_math_expr(msg)))
        if len(queue) >10:
            queue.pop(0)
        send(queue, broadcast=True)

@app.route('/')
def index():
	if queue:
		return render_template('index.html',value=queue)
	return render_template('index.html')

if __name__ == '__main__':
	socketio.run(app)