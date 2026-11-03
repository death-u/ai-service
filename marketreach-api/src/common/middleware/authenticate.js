
import { AppError } from "../errors/AppError.js";
import { authRepository } from "../../modules/auth/repositories/auth.repository.js";
import { verifyAccessToken } from "../../modules/auth/utils/auth.tokens.js";

export async function authenticate(req, res, next) {
  try {
    const authorization = req.headers.authorization;

    if (!authorization?.startsWith("Bearer ")) {
      throw new AppError("Authentication required", 401);
    }

    const token = authorization.slice(7).trim();

    if (!token) {
      throw new AppError("Authentication required", 401);
    }

    let decoded;

    try {
      decoded = verifyAccessToken(token);
    } catch {
      throw new AppError("Invalid or expired access token", 401);
    }

    if (
      !decoded ||
      typeof decoded !== "object" ||
      !decoded.sub
    ) {
      throw new AppError("Invalid access token", 401);
    }

    const user = await authRepository.findById(decoded.sub);

    if (!user || !user.isActive) {
      throw new AppError("Account is unavailable", 401);
    }

    req.user = {
      id: user._id.toString(),
      email: user.email,
      role: user.role,
    };

    next();
  } catch (error) {
    next(error);
  }
}
