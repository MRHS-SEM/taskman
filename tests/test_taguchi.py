def factorial(n):
    """Compute the factorial of n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative values")
    result = 1
    for i in range(1, n+1):
        result *= i
    return result

def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(2) == 2
    assert factorial(5) == 120
    with pytest.raises(ValueError):
        factorial(-1)     