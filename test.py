def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def compute_expression(x, y):
    # Example: (x + y) * (x - y)
    return (x + y) * (x - y)

if __name__ == "__main__":
    x = 10
    y = 4

    print(f"Addition: {x} + {y} = {add(x, y)}")
    print(f"Multiplication: {x} * {y} = {multiply(x, y)}")
    print(f"Expression (x+y)*(x-y): {compute_expression(x, y)}")
