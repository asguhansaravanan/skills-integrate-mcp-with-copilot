import getpass
import json
from pathlib import Path

from app import hash_password


TEACHER_FILE = Path(__file__).with_name("teachers.json")


def main() -> None:
    username = input("Teacher username: ").strip()
    if not username:
        raise SystemExit("A username is required.")

    password = getpass.getpass("Teacher password: ")
    if not password:
        raise SystemExit("A password is required.")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    if TEACHER_FILE.exists():
        data = json.loads(TEACHER_FILE.read_text(encoding="utf-8"))
    else:
        data = {"teachers": []}

    teachers = data.setdefault("teachers", [])
    teachers[:] = [teacher for teacher in teachers if teacher["username"] != username]
    teachers.append({"username": username, "password_hash": hash_password(password)})
    TEACHER_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Teacher account configured for {username}.")


if __name__ == "__main__":
    main()