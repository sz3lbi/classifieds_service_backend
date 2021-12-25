from sqlalchemy.orm.session import Session
from starlette.testclient import TestClient

from app.models.category import Category
from app.models.user import User
from tests.utils import get_jwt_header


class TestGetCategories:
    def test_get_categories_not_logged_in(
        self, db: Session, client: TestClient, create_user, create_category
    ):
        user: User = create_user()
        create_category(user=user)
        resp = client.get("/categories")
        assert resp.status_code == 200
        assert resp.headers["Content-Range"] == "0-1/1"
        assert len(resp.json()) == 1

    def test_get_categories(
        self, db: Session, client: TestClient, create_user, create_category
    ):
        user: User = create_user()
        create_category(user=user)
        jwt_header = get_jwt_header(user)
        resp = client.get("/categories", headers=jwt_header)
        assert resp.status_code == 200
        assert resp.headers["Content-Range"] == "0-2/2"
        assert len(resp.json()) == 2


class TestGetSingleCategory:
    def test_get_single_category(
        self, db: Session, client: TestClient, create_user, create_category
    ):
        user: User = create_user()
        category: Category = create_category(user=user)
        jwt_header = get_jwt_header(user)
        resp = client.get(f"/categories/{category.id}", headers=jwt_header)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id"] == category.id
        assert data["name"] == category.name
        assert data["description"] == category.description


class TestCreateCategory:
    def test_create_category(self, db: Session, client: TestClient, create_user):
        user: User = create_user()
        jwt_header = get_jwt_header(user)

        resp = client.post(
            "/categories",
            headers=jwt_header,
            json={"name": "name", "description": "description"},
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["id"]


class TestDeleteCategory:
    def test_delete_own_category(
        self, db: Session, client: TestClient, create_user, create_category
    ):
        user: User = create_user()
        category: Category = create_category(user=user)
        jwt_header = get_jwt_header(user)

        resp = client.delete(f"/categories/{category.id}", headers=jwt_header)
        assert resp.status_code == 200

    def test_delete_category_does_not_exist(
        self, db: Session, client: TestClient, create_user
    ):
        user: User = create_user()
        jwt_header = get_jwt_header(user)

        resp = client.delete(f"/categories/{10**6}", headers=jwt_header)
        assert resp.status_code == 404, resp.text


class TestUpdateCategory:
    def test_update_own_category(
        self, db: Session, client: TestClient, create_user, create_category
    ):
        user: User = create_user()
        category: Category = create_category(user=user)
        jwt_header = get_jwt_header(user)

        resp = client.put(
            f"/categories/{category.id}",
            headers=jwt_header,
            json={"name": "new name", "description": "new description"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["name"] == "new name"
        assert resp.json()["description"] == "new description"
