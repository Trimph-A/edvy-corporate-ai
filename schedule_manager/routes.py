from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import datetime
from schedule_manager.superuser_manager import add_superuser, get_superusers
from schedule_manager.group_manager import create_group, list_groups

# Router setup
router = APIRouter()

# Data models
class SuperuserRequest(BaseModel):
    email: str

class GroupRequest(BaseModel):
    group_name: str
    members: List[str]

# Superuser Management Endpoints
@router.post("/add-superuser")
async def add_superuser_endpoint(request: SuperuserRequest):
    """
    Endpoint to add a superuser.
    """
    response = add_superuser(request.email)
    return response

# Group Management Endpoints
@router.post("/create-group")
async def create_group_endpoint(request: GroupRequest):
    """
    Endpoint to create a new group of superusers.
    """
    try:
        response = create_group(request.group_name, request.members)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list-groups")
async def list_groups_endpoint():
    """
    Endpoint to list all groups and their members.
    """
    return list_groups()
