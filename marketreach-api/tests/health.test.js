
import { describe, it, expect } from "vitest";
import request from "supertest";
import { app } from "../src/app.js";

describe("MarketReach AI API", () => {
  it("should return API information", async () => {
    const response = await request(app).get("/");

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.version).toBe("1.0.0");
  });

  it("should return 404 for unknown routes", async () => {
    const response = await request(app).get(
      "/api/v1/unknown-route"
    );

    expect(response.status).toBe(404);
    expect(response.body.success).toBe(false);
  });
});
