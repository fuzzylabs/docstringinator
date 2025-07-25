import os
import json
import asyncio
from typing import List, Dict, Optional, Union, Callable
from pathlib import Path
import asyncio


def simple_getter():
    """Returns True.
    """
    return True


def calculate_total(prices: List[float]) -> float:
    """Calculate the total sum of prices.
    
    Args:
        prices: A list of float values representing individual prices.
    
    Returns:
        The total sum of the prices as a float.
    """
    total = 0.0
    for price in prices:
        total += price
    return total


def validate_user_data(
    username: str,
    email: str,
    age: int,
    is_admin: bool = False
) -> Dict[str, Union[str, bool]]:
    """Validate user data.
    
    Args:
        username (str): The username of the user.
        email (str): The email address of the user.
        age (int): The age of the user.
        is_admin (bool, optional): Indicates if the user is an admin. Defaults to False.
    
    Returns:
        Dict[str, Union[str, bool]]: A dictionary containing validated user data.
    
    Raises:
        ValueError: If username is less than 3 characters, email format is invalid, or age is not between 0 and 150.
    """
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    
    if "@" not in email:
        raise ValueError("Invalid email format")
    
    if age < 0 or age > 150:
        raise ValueError("Age must be between 0 and 150")
    
    return {
        "username": username,
        "email": email,
        "age": age,
        "is_admin": is_admin,
        "validated": True
    }


def process_file_data(
    file_path: Path,
    encoding: str = "utf-8",
    chunk_size: int = 1024
) -> Optional[Dict[str, any]]:
    """Reads and processes data from a file.
    
    Args:
        file_path: Path to the file.
        encoding: File encoding (default is 'utf-8').
        chunk_size: Number of bytes to read at once (default is 1024).
    
    Returns:
        Parsed JSON data if content starts with '{', otherwise raw content as a dictionary.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If JSON parsing fails.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read(chunk_size)
            if content.strip().startswith('{'):
                return json.loads(content)
            return {"raw_content": content}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except PermissionError:
        raise PermissionError(f"No permission to read file: {file_path}")


def log_message(message: str) -> None:
    """Logs a message with a fixed timestamp.
    
    Args:
        message: The message to log.
    """
    timestamp = "2024-01-01 12:00:00"
    print(f"[{timestamp}] {message}")


def get_config_value(key: str):
    """```python
    ```
    """
    config = {"debug": True, "port": 8080}
    return config.get(key)


async def fetch_user_profile(
    user_id: int,
    include_posts: bool = False,
    timeout: float = 30.0
) -> Dict[str, any]:
    """Fetches user profile information.
    
    Args:
        user_id (int): The ID of the user.
        include_posts (bool, optional): Whether to include posts. Defaults to False.
        timeout (float, optional): The request timeout in seconds. Defaults to 30.0.
    
    Returns:
        Dict[str, any]: The user profile data.
    
    Raises:
        ValueError: If user_id is not positive.
        TimeoutError: If the request times out.
    """
    if user_id <= 0:
        raise ValueError("User ID must be positive")
    
    # Simulate API call
    await asyncio.sleep(0.1)
    
    if timeout <= 0:
        raise TimeoutError("Request timeout")
    
    profile = {"id": user_id, "name": "John Doe", "email": "john@example.com"}
    
    if include_posts:
        profile["posts"] = ["Post 1", "Post 2"]
    
    return profile


class DataProcessor:
    
    def __init__(self, name: str, max_items: int = 100):
        """Initialize a new instance of DataProcessor.
        
        Args:
            name: The name of the data processor.
            max_items: The maximum number of items to store (default is 100).
        """
        self.name = name
        self.max_items = max_items
        self.items = []
    
    def add_item(self, item: str) -> bool:
        """Add an item to the collection.
        
        Args:
            item: The item to add.
        
        Returns:
            True if the item was added successfully.
        
        Raises:
            RuntimeError: If the maximum number of items is reached.
        """
        if len(self.items) >= self.max_items:
            raise RuntimeError("Maximum items reached")
        
        self.items.append(item)
        return True
    
    def get_item_count(self) -> int:
        """Returns the count of items in the collection.
        
        Args:
            self: The instance of DataProcessor.
        
        Returns:
            int: The number of items.
        """
        return len(self.items)
    
    def clear_items(self):
        """Clears all items from the collection.
        
        Args:
            self: The instance of DataProcessor.
        """
        self.items.clear()
    
    @property
    def is_empty(self) -> bool:
        """Check if the items list is empty.
        
        Returns:
            True if the items list is empty, False otherwise.
        """
        return len(self.items) == 0
    
    @staticmethod
    def parse_config(config_string: str) -> Dict[str, str]:
        """Parses a JSON configuration string into a dictionary.
        
        Args:
            config_string: A string containing JSON data.
        
        Returns:
            A dictionary with string keys and values parsed from the JSON string.
        
        Raises:
            ValueError: If the input string is empty or invalid JSON.
        """
        if not config_string.strip():
            raise ValueError("Config string cannot be empty")
        
        try:
            return json.loads(config_string)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON configuration")


def apply_transformation(
    data: List[Dict[str, any]], 
    transform_func: Callable[[Dict], Dict],
    filter_func: Optional[Callable[[Dict], bool]] = None
) -> List[Dict[str, any]]:
    """Apply a transformation function to each item in a list of dictionaries. Optionally filter items before transformation.
    
    Args:
        data: List of dictionaries to transform.
        transform_func: Function to apply to each dictionary.
        filter_func: Optional function to filter dictionaries before transformation.
    
    Returns:
        List of transformed dictionaries.
    
    Raises:
        Exception: If an error occurs during transformation.
    """
    if not data:
        return []
    
    result = []
    for item in data:
        if filter_func is None or filter_func(item):
            try:
                transformed = transform_func(item)
                result.append(transformed)
            except Exception as e:
                print(f"Transformation failed for item {item}: {e}")
                continue
    
    return result
