"""
Unit tests for json_utils module.
"""

from libriscribe2.utils.json_utils import (
    JSONProcessor,
)


class TestJSONProcessor:
    """Test cases for JSONProcessor class."""

    def test_flatten_nested_dict(self):
        """Test flattening nested dictionaries."""
        # Arrange
        nested_data = {
            "title": "Test Book",
            "author": {"name": "Test Author", "bio": "A test author"},
            "metadata": {"genre": "Fiction", "pages": 300},
        }

        # Act
        result = JSONProcessor.flatten_nested_dict(nested_data)

        # Assert
        assert result["title"] == "Test Book"
        assert "name: Test Author" in result["author"]
        assert "bio: A test author" in result["author"]
        assert "genre: Fiction" in result["metadata"]
        assert "pages: 300" in result["metadata"]

    def test_normalize_dict_keys(self):
        """Test normalizing dictionary keys to lowercase."""
        # Arrange
        data = {"Title": "Test Book", "Author": "Test Author", "Genre": "Fiction"}

        # Act
        result = JSONProcessor.normalize_dict_keys(data)

        # Assert
        assert "title" in result
        assert "author" in result
        assert "genre" in result
        assert result["title"] == "Test Book"

    def test_validate_json_structure_valid(self):
        """Test JSON structure validation with valid data."""
        # Arrange
        data = {"title": "Test Book", "author": "Test Author"}

        # Act
        result = JSONProcessor.validate_json_structure(data, dict)

        # Assert
        assert result is True

    def test_validate_json_structure_invalid(self):
        """Test JSON structure validation with invalid data."""
        # Arrange
        data = "not a dict"

        # Act
        result = JSONProcessor.validate_json_structure(data, dict)

        # Assert
        assert result is False

    def test_validate_json_structure_empty_dict(self):
        """Test JSON structure validation with empty dict."""
        # Arrange
        data = {}

        # Act
        result = JSONProcessor.validate_json_structure(data, dict)

        # Assert
        assert result is False

    def test_safe_json_dumps_valid(self):
        """Test safe JSON dumping with valid data."""
        # Arrange
        data = {"title": "Test Book", "author": "Test Author"}

        # Act
        result = JSONProcessor.safe_json_dumps(data)

        # Assert
        assert result is not None
        assert '"title": "Test Book"' in result
        assert '"author": "Test Author"' in result

    def test_safe_json_dumps_invalid(self):
        """Test safe JSON dumping with invalid data."""

        # Arrange
        class NonSerializable:
            pass

        data = {"test": NonSerializable()}

        # Act
        result = JSONProcessor.safe_json_dumps(data)

        # Assert
        assert result == "{}"

    def test_safe_json_loads_valid(self):
        """Test safe JSON loading with valid JSON."""
        # Arrange
        json_string = '{"title": "Test Book", "author": "Test Author"}'

        # Act
        result = JSONProcessor.safe_json_loads(json_string)

        # Assert
        assert result is not None
        assert result.get("title") == "Test Book"
        assert result.get("author") == "Test Author"

    def test_safe_json_loads_invalid(self):
        """Test safe JSON loading with invalid JSON."""
        # Arrange
        invalid_json = '{"title": "Test Book", "author": "Test Author",}'

        # Act
        result = JSONProcessor.safe_json_loads(invalid_json)

        # Assert
        assert result is None

    def test_safe_json_loads_empty(self):
        """Test safe JSON loading with empty string."""
        # Arrange
        empty_string = ""

        # Act
        result = JSONProcessor.safe_json_loads(empty_string)

        # Assert
        assert result is None

    def test_merge_json_objects(self):
        """Test merging JSON objects."""
        # Arrange
        obj1 = {"title": "Test Book", "author": "Test Author"}
        obj2 = {"genre": "Fiction", "pages": 300}

        # Act
        result = JSONProcessor.merge_json_objects(obj1, obj2)

        # Assert
        assert result.get("title") == "Test Book"
        assert result.get("author") == "Test Author"
        assert result.get("genre") == "Fiction"
        assert result.get("pages") == 300

    def test_merge_json_objects_overwrite(self):
        """Test merging JSON objects with overwriting."""
        # Arrange
        obj1 = {"title": "Test Book", "author": "Test Author"}
        obj2 = {"title": "Updated Book", "genre": "Fiction"}

        # Act
        result = JSONProcessor.merge_json_objects(obj1, obj2)

        # Assert
        assert result.get("title") == "Updated Book"
        assert result.get("author") == "Test Author"
        assert result.get("genre") == "Fiction"

    def test_extract_list_from_json_valid(self):
        """Test extracting list from JSON with valid list."""
        # Arrange
        data = {"chapters": ["Chapter 1", "Chapter 2", "Chapter 3"]}

        # Act
        result = JSONProcessor.extract_list_from_json(data, "chapters")

        # Assert
        assert result == ["Chapter 1", "Chapter 2", "Chapter 3"]

    def test_extract_list_from_json_string(self):
        """Test extracting list from JSON with comma-separated string."""
        # Arrange
        data = {"chapters": "Chapter 1, Chapter 2, Chapter 3"}

        # Act
        result = JSONProcessor.extract_list_from_json(data, "chapters")

        # Assert
        assert result == ["Chapter 1", "Chapter 2", "Chapter 3"]

    def test_extract_list_from_json_missing_key(self):
        """Test extracting list from JSON with missing key."""
        # Arrange
        data = {"title": "Test Book"}

        # Act
        result = JSONProcessor.extract_list_from_json(data, "chapters")

        # Assert
        assert result == []

    def test_extract_list_from_json_default(self):
        """Test extracting list from JSON with default value."""
        # Arrange
        data = {"title": "Test Book"}
        default = ["Default Chapter"]

        # Act
        result = JSONProcessor.extract_list_from_json(data, "chapters", default)

        # Assert
        assert result == default

    def test_extract_string_from_json_valid(self):
        """Test extracting string from JSON."""
        # Arrange
        data = {"title": "Test Book"}

        # Act
        result = JSONProcessor.extract_string_from_json(data, "title")

        # Assert
        assert result == "Test Book"

    def test_extract_string_from_json_missing_key(self):
        """Test extracting string from JSON with missing key."""
        # Arrange
        data = {"author": "Test Author"}

        # Act
        result = JSONProcessor.extract_string_from_json(data, "title")

        # Assert
        assert result == ""

    def test_extract_string_from_json_default(self):
        """Test extracting string from JSON with default value."""
        # Arrange
        data = {"author": "Test Author"}

        # Act
        result = JSONProcessor.extract_string_from_json(data, "title", "Default Title")

        # Assert
        assert result == "Default Title"

    def test_extract_int_from_json_valid(self):
        """Test extracting integer from JSON."""
        # Arrange
        data = {"pages": 300}

        # Act
        result = JSONProcessor.extract_int_from_json(data, "pages")

        # Assert
        assert result == 300

    def test_extract_int_from_json_string(self):
        """Test extracting integer from JSON string."""
        # Arrange
        data = {"pages": "300"}

        # Act
        result = JSONProcessor.extract_int_from_json(data, "pages")

        # Assert
        assert result == 300

    def test_extract_int_from_json_invalid_string(self):
        """Test extracting integer from invalid JSON string."""
        # Arrange
        data = {"pages": "invalid"}

        # Act
        result = JSONProcessor.extract_int_from_json(data, "pages")

        # Assert
        assert result == 0

    def test_validate_required_fields_valid(self):
        """Test validating required fields with all present."""
        # Arrange
        data = {"title": "Test Book", "author": "Test Author", "genre": "Fiction"}
        required_fields = ["title", "author"]

        # Act
        result = JSONProcessor.validate_required_fields(data, required_fields)

        # Assert
        assert result == []

    def test_validate_required_fields_missing(self):
        """Test validating required fields with missing fields."""
        # Arrange
        data = {"title": "Test Book"}
        required_fields = ["title", "author", "genre"]

        # Act
        result = JSONProcessor.validate_required_fields(data, required_fields)

        # Assert
        assert "author" in result
        assert "genre" in result

    def test_validate_required_fields_empty_values(self):
        """Test validating required fields with empty values."""
        # Arrange
        data = {"title": "", "author": "Test Author", "genre": None}
        required_fields = ["title", "author", "genre"]

        # Act
        result = JSONProcessor.validate_required_fields(data, required_fields)

        # Assert
        assert "title" in result
        assert "genre" in result
        assert "author" not in result

    def test_clean_json_data(self):
        """Test cleaning JSON data."""
        # Arrange
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "empty": "",
            "none": None,
            "whitespace": "   ",
            "valid": "Valid Value",
        }

        # Act
        result = JSONProcessor.clean_json_data(data)

        # Assert
        assert "title" in result
        assert "author" in result
        assert "valid" in result
        assert "empty" not in result
        assert "none" not in result
        assert "whitespace" not in result
