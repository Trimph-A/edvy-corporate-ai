superusers = []  # In-memory list of superuser emails

def add_superuser(email: str):
    """
    Adds a new superuser to the list.
    """
    if email not in superusers:
        superusers.append(email)
        return {"message": f"Superuser {email} added successfully."}
    return {"message": f"Superuser {email} already exists."}

def get_superusers():
    """
    Returns the list of all superusers.
    """
    return superusers
