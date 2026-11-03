
import { env } from "../../config/env.js";
import { logger } from "../../config/logger.js";

export function errorHandler(err, req, res, next) {
  if (res.headersSent) {
    return next(err);
  }

  let statusCode = err.statusCode || 500;
  let message = err.message || "Internal server error";
  let details = err.details || undefined;

  if (err.name === "ValidationError") {
    statusCode = 400;
    message = "Database validation failed";
    details = undefined;
  }

  if (err.name === "CastError") {
    statusCode = 400;
    message = "Invalid resource identifier";
    details = undefined;
  }

  if (err.code === 11000) {
    statusCode = 409;
    message = "A resource with this value already exists";
    details = undefined;
  }

  if (statusCode >= 500) {
    logger.error({ err }, "Unhandled application error");

    if (env.NODE_ENV === "production") {
      message = "Internal server error";
      details = undefined;
    }
  }

  return res.status(statusCode).json({
    success: false,
    message,
    ...(details ? { errors: details } : {}),
    ...(env.NODE_ENV === "development"
      ? { stack: err.stack }
      : {}),
  });
}
