import math
def f(x):
    # Define your function here
    return math.log(x)  # Example: f(x) = e^x

def export_values_to_txt(filename, values):
    with open(filename, 'w') as file:
        for x, fx in enumerate(values):
            file.write(f"{x},{fx}\n")

# Example usage
values_to_export = [f(x) for x in range(1,21)]  # Replace range(10) with your desired range
export_values_to_txt('IV.txt', values_to_export)