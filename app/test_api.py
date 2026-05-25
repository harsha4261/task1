import pytest
from contextlib import contextmanager
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from .database import Base, get_db
from .main import app
from . import models


@contextmanager
def get_postgres_container():
    container = PostgresContainer("postgres:15")
    try:
        container.start()
        print("\nContainer Started")
        yield container
    finally:
        print("\nStopping Container")
        container.stop()

@pytest.fixture(scope="session")
def postgres_container():
    with get_postgres_container() as container:
        yield container



@pytest.fixture(scope="function")
def db_session(postgres_container):
    DATABASE_URL = postgres_container.get_connection_url()
    engine = create_engine(DATABASE_URL)
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)





@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c






def test_read_root(client):

    response = client.get("/")

    assert response.status_code == 200


def test_create_item(client):

    response = client.post(
        "/posts",
        json={
            "title": "this is my first test",
            "content": "this is the content of the first api test",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "this is my first test"
    assert data["content"] == "this is the content of the first api test"
    assert "id" in data


def test_get_all_posts(client):

    client.post(
        "/posts",
        json={
            "title": "sample title",
            "content": "sample content"
        }
    )

    response = client.get("/posts")

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_get_single_post(client):

    created_post = client.post(
        "/posts",
        json={
            "title": "single test",
            "content": "single content"
        },
    )

    post_id = created_post.json()["id"]

    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["post_detail"]["id"] == post_id
    assert data["post_detail"]["title"] == "single test"
    assert data["post_detail"]["content"] == "single content"


def test_get_non_existing_post(client):

    response = client.get("/posts/99")

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "post with id: 99 was not found"
    )


def test_get_latest_post(client):

    client.post(
        "/posts",
        json={
            "title": "latest post",
            "content": "latest content"
        }
    )

    response = client.get("/posts/latest")

    assert response.status_code == 200

    data = response.json()

    assert "latest_post" in data


def test_update_post(client):

    created_post = client.post(
        "/posts",
        json={
            "title": "old title",
            "content": "old content"
        },
    )

    post_id = created_post.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "updated title",
            "content": "updated content",
            "published": True,
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert data["data"]["title"] == "updated title"
    assert data["data"]["content"] == "updated content"


def test_update_non_existing_post(client):

    response = client.put(
        "/posts/999999",
        json={
            "title": "updated title",
            "content": "updated content",
            "published": True,
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "post with id: 999999 was not found"
    )


def test_delete_post(client):

    created_post = client.post(
        "/posts",
        json={
            "title": "delete title",
            "content": "delete content"
        },
    )

    post_id = created_post.json()["id"]

    response = client.delete(f"/posts/{post_id}")

    assert response.status_code == 204


def test_delete_non_existing_post(client):

    response = client.delete("/posts/99")

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "post with id: 99 was not found"
    )
