#!/usr/bin/env python3
"""
Clear SQLite database for testing
"""
import os

# SQLite DB file
db_file = "test.db"

if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✅ Removed {db_file}")
else:
    print(f"ℹ️ {db_file} doesn't exist")

# Remove other test databases
test_dbs = ["potenday.db", "app.db", "test.sqlite", "development.db"]
for db in test_dbs:
    if os.path.exists(db):
        os.remove(db)
        print(f"✅ Removed {db}")

print("\n✅ Database cleaned for fresh testing!")