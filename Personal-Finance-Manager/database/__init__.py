"""Database package for SQLite connection management, schema setup, and mock data seeding."""

from database.db_manager import get_connection, init_db, seed_mock_data

__all__ = ["get_connection", "init_db", "seed_mock_data"]
