from typing import Optional


class SafeFieldUpdater:
    def __init__(self, target_object):
        self.target = target_object
        self.updated_fields = []

    def update_string_field(
        self, field_name: str, new_value: Optional[str], max_length: int = 500
    ) -> bool:
        if new_value is None or not hasattr(self.target, field_name):
            return False

        if not isinstance(new_value, str) or len(new_value) > max_length:
            return False

        if getattr(self.target, field_name) != new_value:
            setattr(self.target, field_name, new_value)
            self.updated_fields.append(field_name)
            return True
        return False

    def update_int_field(
        self,
        field_name: str,
        new_value: Optional[int],
        min_val: int = 0,
        max_val: int = 1000,
    ) -> bool:
        if new_value is None or not hasattr(self.target, field_name):
            return False

        if not isinstance(new_value, int) or not (min_val <= new_value <= max_val):
            return False

        if getattr(self.target, field_name) != new_value:
            setattr(self.target, field_name, new_value)
            self.updated_fields.append(field_name)
            return True
        return False

    def update_enum_field(
        self, field_name: str, new_value: Optional[str], valid_values: list
    ) -> bool:
        if new_value is None or not hasattr(self.target, field_name):
            return False

        if not isinstance(new_value, str) or new_value not in valid_values:
            return False

        if getattr(self.target, field_name) != new_value:
            setattr(self.target, field_name, new_value)
            self.updated_fields.append(field_name)
            return True
        return False
