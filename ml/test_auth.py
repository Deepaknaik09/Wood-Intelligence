import unittest
import os
import shutil
import tempfile
from ml import auth

class TestAuth(unittest.TestCase):
    def setUp(self):
        # Create a fresh temp test database
        self.temp_dir = tempfile.mkdtemp()
        self.orig_db_path = auth.DB_PATH
        auth.DB_PATH = os.path.join(self.temp_dir, "test_users.db")
        auth.init_db()

    def tearDown(self):
        auth.DB_PATH = self.orig_db_path
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_seed_user(self):
        user, msg = auth.authenticate_user("inspector", "timber123")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "inspector")
        self.assertEqual(user["role"], "Timber Quality Inspector")
        self.assertTrue(user["is_authenticated"])

    def test_register_and_authenticate(self):
        ok, msg = auth.register_user("john_doe", "secret99", "John Doe", "Master Joiner / Carpenter")
        self.assertTrue(ok)
        
        # Test valid login
        user, msg = auth.authenticate_user("john_doe", "secret99")
        self.assertIsNotNone(user)
        self.assertEqual(user["full_name"], "John Doe")
        self.assertEqual(user["role"], "Master Joiner / Carpenter")

        # Test wrong password
        bad_user, bad_msg = auth.authenticate_user("john_doe", "wrongpassword")
        self.assertIsNone(bad_user)
        self.assertIn("Invalid password", bad_msg)

    def test_duplicate_username(self):
        ok, _ = auth.register_user("duplicate_user", "pass1234", "User 1", "Timber Quality Inspector")
        self.assertTrue(ok)
        ok2, msg2 = auth.register_user("duplicate_user", "pass5678", "User 2", "Timber Quality Inspector")
        self.assertFalse(ok2)
        self.assertIn("already registered", msg2)

    def test_short_password(self):
        ok, msg = auth.register_user("short_pass", "123", "Shorty", "Timber Quality Inspector")
        self.assertFalse(ok)
        self.assertIn("at least 6 characters", msg)

if __name__ == "__main__":
    unittest.main()
