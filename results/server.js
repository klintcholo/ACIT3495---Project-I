const express = require("express");
const { MongoClient } = require("mongodb");
const path = require("path");

const PORT = 3001;

function createApp(statistics, database) {
  const app = express();

  // Webseite bereitstellen
  app.use(express.static(path.join(__dirname, "public")));

  // Aktuelle Statistiken abrufen
  app.get("/api/statistics", async (req, res) => {
    try {
      const result = await statistics.findOne({
        _id: "latest"
      });

      if (!result) {
        return res.status(404).json({
          error: "No statistics available yet"
        });
      }

      res.json(result);
    } catch (error) {
      console.error("MongoDB error:", error.message);
      res.status(503).json({
        error: "Statistics currently unavailable"
      });
    }
  });

  // Healthcheck
  app.get("/health", async (req, res) => {
    try {
      await database.admin().ping();
      res.json({ status: "ok" });
    } catch {
      res.status(503).json({
        status: "unhealthy"
      });
    }
  });

  return app;
}

if (require.main === module) {
  if (!process.env.MONGO_URI) {
    throw new Error("MONGO_URI environment variable is required");
  }

  const client = new MongoClient(process.env.MONGO_URI, {
    serverSelectionTimeoutMS: 5000
  });

  const database = client.db("analytics");
  const statistics = database.collection("statistics");
  const app = createApp(statistics, database);

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Results Service running on port ${PORT}`);
  });
}

module.exports = { createApp };

