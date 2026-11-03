
import express from "express";
import cors from "cors";
import helmet from "helmet";
import compression from "compression";
import cookieParser from "cookie-parser";
import rateLimit from "express-rate-limit";
import pinoHttp from "pino-http";

import { env } from "./config/env.js";
import { logger } from "./config/logger.js";

import apiRoutes from "./routes/index.js";
import { notFound } from "./common/middleware/notFound.js";
import { errorHandler } from "./common/middleware/errorHandler.js";

export const app = express();

app.disable("x-powered-by");
app.set("trust proxy", env.TRUST_PROXY);

app.use(helmet());

app.use(
  cors({
    origin: env.CLIENT_URL,
    credentials: true,
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

app.use(
  pinoHttp({
    logger,
    autoLogging: env.NODE_ENV !== "test",
  })
);

app.use(compression());
app.use(express.json({ limit: "1mb" }));
app.use(express.urlencoded({ extended: true, limit: "1mb" }));
app.use(cookieParser());

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 200,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  message: {
    success: false,
    message: "Too many requests. Please try again later.",
  },
});

app.get("/", (req, res) => {
  res.json({
    success: true,
    message: "Welcome to MarketReach AI API",
    version: "1.0.0",
    health: `${env.API_PREFIX}/health`,
  });
});

app.use(env.API_PREFIX, apiLimiter, apiRoutes);

app.use(notFound);
app.use(errorHandler);
