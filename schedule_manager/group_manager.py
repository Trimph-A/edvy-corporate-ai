from typing import Dict, List

# In-memory store for groups
groups: Dict[str, List[str]] = {}

def create_group(group_name: str, members: List[str]) -> dict:
    """
    Creates a group of superusers.
    """
    if group_name in groups:
        return {"message": f"Group {group_name} already exists."}
    groups[group_name] = members
    return {"message": f"Group {group_name} created successfully.", "members": members}

def list_groups() -> dict:
    """
    Lists all groups and their members.
    """
    return {"groups": groups}

def get_group_members(group_name: str) -> List[str]:
    """
    Returns members of a specific group.
    """
    if group_name not in groups:
        raise ValueError(f"Group {group_name} does not exist.")
    return groups[group_name]
