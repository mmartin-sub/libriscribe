"""Simple test to verify CI workflow functionality."""

def test_basic_functionality():
    """Test basic functionality - should always pass."""
    assert 1 + 1 == 2

def test_string_operations():
    """Test string operations - should always pass."""
    text = "Hello World"
    assert text.upper() == "HELLO WORLD"
    assert text.lower() == "hello world"

def test_list_operations():
    """Test list operations - should always pass."""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert sum(numbers) == 15
    assert max(numbers) == 5