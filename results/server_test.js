
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { createApp } = require("./server");

async function withServer(statistics, database, runTest) {
  const app = createApp(statistics, database);

  const server = app.listen(0, "127.0.0.1");

  await new Promise((resolve) => server.once("listening", resolve));

  try {
    const address = server.address();
    const response = await fetch(
      `http://127.0.0.1:${address.port}`
    );
    await runTest(response);
  } finally {
    await new Promise((resolve, reject) => {
      server.close((error) => {
        if (error) reject(error);
        else resolve();
      });
    });
  }
}

test("GET /api/statistics returns stored statistics", async () => {
  const expected = {
    _id: "latest",
    count: 4,
    minimum: 70,
    maximum: 100,
    average: 85
  };

  const statistics = {
    findOne: async () => expected
  };

  const database = {
    admin: () => ({ ping: async () => ({ ok: 1 }) })
  };

  const app = createApp(statistics, database);
  const server = app.listen(0, "127.0.0.1");

  await new Promise((resolve) => server.once("listening", resolve));

  try {
    const response = await fetch(
      `http://127.0.0.1:${server.address().port}/api/statistics`
    );

    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), expected);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("GET /api/statistics returns 404 when no statistics exist", async () => {
  const statistics = { findOne: async () => null };
  const database = {
    admin: () => ({ ping: async () => ({ ok: 1 }) })
  };

  const app = createApp(statistics, database);
  const server = app.listen(0, "127.0.0.1");

  await new Promise((resolve) => server.once("listening", resolve));

  try {
    const response = await fetch(
      `http://127.0.0.1:${server.address().port}/api/statistics`
    );

    assert.equal(response.status, 404);
    assert.deepEqual(await response.json(), {
      error: "No statistics available yet"
    });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("GET /api/statistics returns 503 when the database fails", async () => {
  const statistics = {
    findOne: async () => {
      throw new Error("Database unavailable");
    }
  };

  const database = {
    admin: () => ({ ping: async () => ({ ok: 1 }) })
  };

  const app = createApp(statistics, database);
  const server = app.listen(0, "127.0.0.1");

  await new Promise((resolve) => server.once("listening", resolve));

  try {
    const response = await fetch(
      `http://127.0.0.1:${server.address().port}/api/statistics`
    );

    assert.equal(response.status, 503);
    assert.deepEqual(await response.json(), {
      error: "Statistics currently unavailable"
    });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("GET /health returns healthy when the database responds", async () => {
  const statistics = { findOne: async () => null };
  const database = {
    admin: () => ({ ping: async () => ({ ok: 1 }) })
  };

  const app = createApp(statistics, database);
  const server = app.listen(0, "127.0.0.1");

  await new Promise((resolve) => server.once("listening", resolve));

  try {
    const response = await fetch(
      `http://127.0.0.1:${server.address().port}/health`
    );

    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { status: "ok" });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("GET /health returns 503 when the database is unavailable", async () => {
  const statistics = { findOne: async () => null };
  const database = {
    admin: () => ({
      ping: async () => {
        throw new Error("Database unavailable");
      }
    })
  };

  const app = createApp(statistics, database);
  const server = app.listen(0, "127.0.0.1");

  await new Promise((resolve) => server.once("listening", resolve));

  try {
    const response = await fetch(
      `http://127.0.0.1:${server.address().port}/health`
    );

    assert.equal(response.status, 503);
    assert.deepEqual(await response.json(), {
      status: "unhealthy"
    });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

