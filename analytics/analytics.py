import os
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import pymysql
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def get_mysql_config():
    return {
        "host": os.environ["MYSQL_HOST"],
        "user": os.environ["MYSQL_USER"],
        "password": os.environ["MYSQL_PASSWORD"],
        "database": os.environ["MYSQL_DATABASE"],
        "connect_timeout": 5
    }

INTERVAL = 30


def calculate_statistics(values):
    if not values:
        return {
            "count": 0,
            "minimum": None,
            "maximum": None,
            "average": None
        }

    return {
        "count": len(values),
        "minimum": min(values),
        "maximum": max(values),
        "average": sum(values) / len(values)
    }


def run_analytics():
    mongo_uri = os.environ["MONGO_URI"]
    connection = pymysql.connect(**get_mysql_config())
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT grade FROM grades")
            rows = cursor.fetchall()
    finally:
        connection.close()

    values = [float(row[0]) for row in rows]

    # 2. Statistiken in Python berechnen
    statistics = calculate_statistics(values)
    statistics["updated_at"] = datetime.now(timezone.utc)

    # 3. Ergebnisse in MongoDB speichern
    with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
        collection = client["analytics"]["statistics"]
        collection.update_one(
            {"_id": "latest"},
            {"$set": statistics},
            upsert=True
        )

    logging.info("Statistics updated: %s", statistics)

if __name__ == "__main__":
    logging.info("Analytics Service started")
    while True:
        try:
            run_analytics()
            Path("/tmp/analytics-healthy").touch()
        except Exception:
            logging.exception("Analytics calculation failed")
        time.sleep(INTERVAL)
