"""API integration tests (real FastAPI TestClient, no mocks)."""

import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.storage import reset_all_stores


@pytest.fixture()
def client():
    reset_all_stores()
    return TestClient(create_app())


@pytest.fixture()
def auth(client):
    client.post("/api/auth/register", json={
        "username": "director", "email": "d@oiioii.test", "password": "secret123"})
    token = client.post("/api/auth/login", json={
        "username": "director", "password": "secret123"}).json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_routes_require_auth(client):
    assert client.get("/api/projects").status_code == 401
    assert client.get("/api/projects",
                      headers={"Authorization": "Bearer bogus"}).status_code == 401


def test_register_login_logout(client, auth):
    resp = client.post("/api/auth/logout", headers=auth)
    assert resp.status_code == 204
    assert client.get("/api/projects", headers=auth).status_code == 401


def test_project_crud(client, auth):
    created = client.post("/api/projects", headers=auth,
                          json={"name": "My Film", "description": "noir"})
    assert created.status_code == 201
    project_id = created.json()["id"]

    listed = client.get("/api/projects", headers=auth).json()
    assert [p["id"] for p in listed] == [project_id]

    got = client.get(f"/api/projects/{project_id}", headers=auth)
    assert got.status_code == 200 and got.json()["name"] == "My Film"

    assert client.delete(f"/api/projects/{project_id}",
                         headers=auth).status_code == 204
    assert client.get(f"/api/projects/{project_id}",
                      headers=auth).status_code == 404


def test_project_ownership_enforced(client, auth):
    project_id = client.post("/api/projects", headers=auth,
                             json={"name": "Mine"}).json()["id"]
    client.post("/api/auth/register", json={
        "username": "intruder", "email": "i@oiioii.test", "password": "secret123"})
    other = {"Authorization": "Bearer " + client.post(
        "/api/auth/login", json={"username": "intruder",
                                 "password": "secret123"}).json()["token"]}

    assert client.delete(f"/api/projects/{project_id}",
                         headers=other).status_code == 403
    assert client.post(f"/api/projects/{project_id}/jobs", headers=other,
                       json={"stage": "script"}).status_code == 403


def test_workflow_lifecycle(client, auth):
    project_id = client.post("/api/projects", headers=auth,
                             json={"name": "Flow"}).json()["id"]
    wf = client.post(f"/api/projects/{project_id}/workflows", headers=auth,
                     json={"stages": ["script", "storyboard"]})
    assert wf.status_code == 201
    wf_id = wf.json()["id"]
    assert wf.json()["current_stage"] == "script"

    advanced = client.post(f"/api/workflows/{wf_id}/advance", headers=auth).json()
    assert advanced == {"completed": False, "current_stage": "storyboard"}

    finished = client.post(f"/api/workflows/{wf_id}/advance", headers=auth).json()
    assert finished == {"completed": True, "current_stage": None}


def test_job_lifecycle(client, auth):
    project_id = client.post("/api/projects", headers=auth,
                             json={"name": "Jobs"}).json()["id"]
    job = client.post(f"/api/projects/{project_id}/jobs", headers=auth,
                      json={"stage": "script", "input_data": {"prompt": "hi"}})
    assert job.status_code == 201
    job_id = job.json()["id"]
    assert job.json()["status"] == "pending"

    assert client.post(f"/api/jobs/{job_id}/complete", headers=auth,
                       json={"output_data": {}}).status_code == 409

    started = client.post(f"/api/jobs/{job_id}/start", headers=auth)
    assert started.status_code == 200 and started.json()["status"] == "running"

    completed = client.post(f"/api/jobs/{job_id}/complete", headers=auth,
                            json={"output_data": {"text": "done"}})
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"


def test_unknown_stage_rejected(client, auth):
    project_id = client.post("/api/projects", headers=auth,
                             json={"name": "Bad"}).json()["id"]
    resp = client.post(f"/api/projects/{project_id}/jobs", headers=auth,
                       json={"stage": "warp-drive"})
    assert resp.status_code == 422
