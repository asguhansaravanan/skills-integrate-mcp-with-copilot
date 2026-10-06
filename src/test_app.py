import json
import tempfile
import unittest
from http.cookies import SimpleCookie
from pathlib import Path
from unittest.mock import patch

import app
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response


def make_request(cookie: str = "") -> Request:
    headers = [(b"cookie", cookie.encode("utf-8"))] if cookie else []
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/",
            "query_string": b"",
            "headers": headers,
            "server": ("testserver", 80),
            "client": ("testclient", 1234),
        }
    )


class TeacherAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.password_hash = app.hash_password("correct-horse-battery")

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        config_path = Path(self.temp_dir.name) / "teachers.json"
        config_path.write_text(
            json.dumps(
                {
                    "teachers": [
                        {"username": "teacher", "password_hash": self.password_hash}
                    ]
                }
            ),
            encoding="utf-8",
        )
        patcher = patch.object(app, "TEACHER_FILE", config_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        app.teacher_sessions.clear()

    def test_login_session_and_logout(self) -> None:
        response = Response()
        result = app.login(
            app.LoginRequest(username="teacher", password="correct-horse-battery"),
            make_request(),
            response,
        )
        self.assertTrue(result["authenticated"])
        cookies = SimpleCookie()
        cookies.load(response.headers["set-cookie"])
        token = cookies[app.SESSION_COOKIE].value

        request = make_request(f"{app.SESSION_COOKIE}={token}")
        self.assertEqual(app.require_teacher(request), "teacher")

        app.logout(request, Response())
        with self.assertRaises(HTTPException) as error:
            app.require_teacher(request)
        self.assertEqual(error.exception.status_code, 401)

    def test_invalid_password_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as error:
            app.login(
                app.LoginRequest(username="teacher", password="incorrect"),
                make_request(),
                Response(),
            )
        self.assertEqual(error.exception.status_code, 401)

    def test_only_mutation_routes_require_teacher(self) -> None:
        protected_paths = {
            "/activities/{activity_name}/signup",
            "/activities/{activity_name}/unregister",
        }
        for route in app.app.routes:
            if getattr(route, "path", None) in protected_paths:
                self.assertIn(
                    app.require_teacher,
                    [dependency.call for dependency in route.dependant.dependencies],
                )

    def test_activity_roster_remains_public(self) -> None:
        self.assertIs(app.get_activities(), app.activities)


if __name__ == "__main__":
    unittest.main()