
import { AppError } from "../errors/AppError.js";

export function notFound(req, res, next) {
  next(
    new AppError(
      `Route ${req.method} ${req.originalUrl} not found`,
      404
    )
  );
}
