"""
Project service for managing animation projects.

Provides CRUD operations for projects with user ownership.
"""

from typing import List, Optional
from datetime import datetime
import uuid

from .models import Project
from .storage import projects_store


class ProjectError(Exception):
    """Raised when project operation fails."""
    pass


class ProjectService:
    """Service for managing projects."""

    def create_project(self, user_id: str, name: str, description: str = "") -> Project:
        """Create a new project for a user."""
        if not name or not name.strip():
            raise ProjectError("Project name cannot be empty")
        
        project = Project(
            id=str(uuid.uuid4()),
            name=name.strip(),
            description=description.strip(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        projects_store.add(project.id, project)
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by ID."""
        return projects_store.get(project_id)

    def list_projects(self, user_id: str) -> List[Project]:
        """List all projects for a user."""
        return projects_store.filter(lambda p: p.user_id == user_id and p.is_active)

    def update_project(self, project_id: str, **kwargs) -> Project:
        """Update project fields."""
        project = projects_store.get(project_id)
        if project is None:
            raise ProjectError(f"Project {project_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.updated_at = datetime.utcnow()
        projects_store.add(project.id, project)
        return project

    def delete_project(self, project_id: str) -> None:
        """Delete a project."""
        if not projects_store.delete(project_id):
            raise ProjectError(f"Project {project_id} not found")

    def is_owner(self, project_id: str, user_id: str) -> bool:
        """Check if user owns the project."""
        project = projects_store.get(project_id)
        return project is not None and project.user_id == user_id