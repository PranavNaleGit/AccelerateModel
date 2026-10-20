def is_prime(n: int) -> bool:
    """Return True if n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2

    return True


if __name__ == "__main__":
    assert is_prime(2)
    assert is_prime(17)
    assert not is_prime(1)
    assert not is_prime(21)
    print("All sample checks passed.")
