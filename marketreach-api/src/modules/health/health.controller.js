
import mongoose from "mongoose";

export function getHealth(req, res) {
  const databaseConnected = mongoose.connection.readyState === 1;

  return res.status(databaseConnected ? 200 : 503).json({
    success: databaseConnected,
    message: databaseConnected
      ? "MarketReach AI API is healthy"
      : "Database connection unavailable",
    data: {
      service: "marketreach-backend",
      database: databaseConnected ? "connected" : "disconnected",
      uptime: Math.floor(process.uptime()),
      timestamp: new Date().toISOString(),
    },
  });
}
