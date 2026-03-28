def validate_number(value):
    """
    Validate that the input is a valid number.
    
    Args:
        value: Input to validate
    
    Returns:
        float: Validated number
    
    Raises:
        ValueError: If input cannot be converted to a number
        TypeError: If input is not a numeric type
    """
    try:
        # Try to convert to float to support both integers and decimals
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid input: '{value}' is not a valid number")
    except TypeError:
        raise TypeError(f"Invalid input type: expected a number, got {type(value)}")

def add(a, b):
    """
    Add two numbers with error handling.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        float: Sum of a and b
    
    Raises:
        ValueError: If inputs are not valid numbers
    """
    try:
        # Validate inputs
        a_num = validate_number(a)
        b_num = validate_number(b)
        
        # Perform addition
        return a_num + b_num
    except (ValueError, TypeError) as e:
        print(f"Addition Error: {e}")
        raise

def subtract(a, b):
    """
    Subtract two numbers with error handling.
    
    Args:
        a: Number to subtract from
        b: Number to subtract
    
    Returns:
        float: Result of a - b
    
    Raises:
        ValueError: If inputs are not valid numbers
    """
    try:
        # Validate inputs
        a_num = validate_number(a)
        b_num = validate_number(b)
        
        # Perform subtraction
        return a_num - b_num
    except (ValueError, TypeError) as e:
        print(f"Subtraction Error: {e}")
        raise

def multiply(a, b):
    """
    Multiply two numbers with error handling.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        float: Product of a and b
    
    Raises:
        ValueError: If inputs are not valid numbers
    """
    try:
        # Validate inputs
        a_num = validate_number(a)
        b_num = validate_number(b)
        
        # Perform multiplication
        return a_num * b_num
    except (ValueError, TypeError) as e:
        print(f"Multiplication Error: {e}")
        raise

def divide(a, b):
    """
    Divide two numbers with error handling.
    
    Args:
        a: Numerator
        b: Denominator
    
    Returns:
        float: Result of a divided by b
    
    Raises:
        ValueError: If inputs are not valid numbers
        ZeroDivisionError: If denominator is zero
    """
    try:
        # Validate inputs
        a_num = validate_number(a)
        b_num = validate_number(b)
        
        # Check for division by zero
        if b_num == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        
        # Perform division
        return a_num / b_num
    except (ValueError, TypeError) as e:
        print(f"Division Error: {e}")
        raise
    except ZeroDivisionError as e:
        print(f"Division Error: {e}")
        raise

# Example usage and basic testing
if __name__ == "__main__":
    try:
        print("Calculator Operations Test:")
        print(f"5 + 3 = {add(5, 3)}")
        print(f"10 - 4 = {subtract(10, 4)}")
        print(f"6 * 7 = {multiply(6, 7)}")
        print(f"15 / 3 = {divide(15, 3)}")
        
        # Uncomment to test error handling
        # print(divide(10, 0))  # Will raise ZeroDivisionError
        # print(add("abc", 5))  # Will raise ValueError
    except Exception as e:
        print(f"An error occurred: {e}")