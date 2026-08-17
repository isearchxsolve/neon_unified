"""Tests for Project service."""

import pytest
import sys
import os

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.projects import ProjectService, ProjectError
from src.storage import projects_store
from src.models import Project


@pytest.fixture(autouse=True)
def reset_store():
    projects_store.clear()
    yield
    projects_store.clear()


class TestProjectService:
    def setup_method(self):
        self.service = ProjectService()

    def test_create_project_assigns_id_and_owner(self):
        project = self.service.create_project(user_id="u-1", name="My Film", description="A short film")
        assert isinstance(project, Project)
        assert project.id
        assert project.user_id == "u-1"
        assert project.name == "My Film"

    def test_create_project_defaults_to_active(self):
        project = self.service.create_project(user_id="u-1", name="P")
        assert project.is_active is True

    def test_get_project_returns_existing_project(self):
        project = self.service.create_project(user_id="u-1", name="P")
        fetched = self.service.get_project(project.id)
        assert fetched is not None
        assert fetched.id == project.id

    def test_get_project_unknown_returns_none(self):
        assert self.service.get_project("missing") is None

    def test_list_projects_returns_only_user_projects(self):
        self.service.create_project(user_id="u-1", name="P1")
        self.service.create_project(user_id="u-1", name="P2")
        self.service.create_project(user_id="u-2", name="P3")
        u1_projects = self.service.list_projects(user_id="u-1")
        assert len(u1_projects) == 2

    def test_update_project_modifies_fields(self):
        project = self.service.create_project(user_id="u-1", name="Old")
        updated = self.service.update_project(project.id, name="New", description="D")
        assert updated.name == "New"
        assert updated.description == "D"

    def test_update_unknown_project_raises_error(self):
        with pytest.raises(ProjectError):
            self.service.update_project("missing", name="X")

    def test_delete_project_removes_it(self):
        project = self.service.create_project(user_id="u-1", name="P")
        self.service.delete_project(project.id)
        assert self.service.get_project(project.id) is None

    def test_delete_unknown_project_raises_error(self):
        with pytest.raises(ProjectError):
            self.service.delete_project("missing")

    def test_create_project_rejects_empty_name(self):
        with pytest.raises(ProjectError):
            self.service.create_project(user_id="u-1", name="")
