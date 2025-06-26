"""
Helper Functions

Common utility functions used across the application.
"""

import hashlib
import re
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, unquote

import aiofiles
from fastapi import UploadFile


def generate_random_string(length: int = 32, use_alphanumeric: bool = True) -> str:
    """Generate a random string of specified length"""
    if use_alphanumeric:
        characters = string.ascii_letters + string.digits
    else:
        characters = string.ascii_letters + string.digits + string.punctuation

    return "".join(secrets.choice(characters) for _ in range(length))


def generate_uuid_string() -> str:
    """Generate a UUID-like string"""
    import uuid

    return str(uuid.uuid4())


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase
    text = text.lower()

    # Replace spaces and special characters with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    # Truncate if necessary
    if len(text) > max_length:
        text = text[:max_length].rstrip("-")

    return text


def hash_file_content(content: bytes) -> str:
    """Generate SHA256 hash of file content"""
    return hashlib.sha256(content).hexdigest()


def format_file_size(size_bytes: float) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
    return re.match(pattern, url) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path components
    filename = Path(filename).name

    # Replace unsafe characters
    filename = re.sub(r"[^\w\s.-]", "", filename)

    # Replace multiple spaces with single space
    filename = re.sub(r"\s+", " ", filename)

    # Trim and ensure it's not empty
    filename = filename.strip()
    if not filename:
        filename = f"file_{generate_random_string(8)}"

    return filename


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


def is_allowed_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file type is allowed"""
    extension = get_file_extension(filename)
    return extension in [ext.lower() for ext in allowed_extensions]


async def save_upload_file(
    upload_file: UploadFile, destination_path: Path
) -> Dict[str, Any]:
    """Save uploaded file to destination path"""
    try:
        # Ensure destination directory exists
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        # Read file content
        content = await upload_file.read()

        # Save file
        async with aiofiles.open(destination_path, "wb") as f:
            await f.write(content)

        # Calculate file hash and size
        file_hash = hash_file_content(content)
        file_size = len(content)

        return {
            "filename": upload_file.filename,
            "saved_path": str(destination_path),
            "file_size": file_size,
            "file_hash": file_hash,
            "content_type": upload_file.content_type,
        }

    except Exception as e:
        raise Exception(f"Failed to save file: {str(e)}")


def calculate_pagination(total: int, page: int, per_page: int) -> Dict[str, int]:
    """Calculate pagination metadata"""
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
    }


def parse_sort_params(sort_param: Optional[str]) -> List[Dict[str, str]]:
    """Parse sort parameter string into list of sort criteria"""
    if not sort_param:
        return []

    sort_criteria = []

    for criterion in sort_param.split(","):
        criterion = criterion.strip()
        if not criterion:
            continue

        if criterion.startswith("-"):
            field = criterion[1:]
            order = "desc"
        else:
            field = criterion
            order = "asc"

        sort_criteria.append({"field": field, "order": order})

    return sort_criteria


def parse_filter_params(filter_param: Optional[str]) -> List[Dict[str, Any]]:
    """Parse filter parameter string into list of filter criteria"""
    if not filter_param:
        return []

    filters = []

    # Simple format: field:operator:value,field2:operator2:value2
    for filter_str in filter_param.split(","):
        filter_str = filter_str.strip()
        if not filter_str:
            continue

        parts = filter_str.split(":", 2)
        if len(parts) == 3:
            field, operator, value = parts

            # Try to convert value to appropriate type
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            elif "." in value and value.replace(".", "").isdigit():
                value = float(value)

            filters.append({"field": field, "operator": operator, "value": value})

    return filters


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string to datetime object"""
    return datetime.strptime(dt_str, format_str)


def get_time_ago_string(dt: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2629746:  # ~30.44 days
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31556952:  # ~365.24 days
        months = int(seconds // 2629746)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds // 31556952)
        return f"{years} year{'s' if years != 1 else ''} ago"


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like emails, phone numbers"""
    if len(data) <= visible_chars:
        return mask_char * len(data)

    visible_start = visible_chars // 2
    visible_end = visible_chars - visible_start

    masked_part = mask_char * (len(data) - visible_chars)

    return (
        data[:visible_start] + masked_part + data[-visible_end:]
        if visible_end > 0
        else data[:visible_start] + masked_part
    )


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def clean_html_tags(html_text: str) -> str:
    """Remove HTML tags from text"""
    import re

    clean = re.compile("<.*?>")
    return re.sub(clean, "", html_text)


def generate_color_from_string(text: str) -> str:
    """Generate a consistent color hex code from string"""
    # Create hash from string
    hash_object = hashlib.md5(text.encode())
    hex_hash = hash_object.hexdigest()

    # Take first 6 characters for RGB
    return f"#{hex_hash[:6]}"


def url_encode(text: str) -> str:
    """URL encode text"""
    return quote(text)


def url_decode(text: str) -> str:
    """URL decode text"""
    return unquote(text)


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
