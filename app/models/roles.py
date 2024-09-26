from enum import Enum


# IMPORTANT: ORDER IS IMPORTANT
# EACH ROLE HAS ALL THE PERMISSIONS OF THE ROLE ABOVE IT
# ENSURE ROLE IS IN ORDER OF PRIVILEDGE
class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    ROOT = "root"
