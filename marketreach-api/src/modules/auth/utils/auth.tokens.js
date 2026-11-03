
import crypto from "node:crypto";
import jwt from "jsonwebtoken";
import { env } from "../../../config/env.js";

const REFRESH_TOKEN_DAYS = 7;

export function createAccessToken(user) {
  return jwt.sign(
    {
      role: user.role,
    },
    env.JWT_ACCESS_SECRET,
    {
      subject: user.id.toString(),
      expiresIn: "15m",
      issuer: "marketreach-ai",
      audience: "marketreach-mobile",
      algorithm: "HS256",
    },
  );
}

export function verifyAccessToken(token) {
  return jwt.verify(token, env.JWT_ACCESS_SECRET, {
    issuer: "marketreach-ai",
    audience: "marketreach-mobile",
    algorithms: ["HS256"],
  });
}

export function createRefreshToken() {
  const token = crypto.randomBytes(48).toString("hex");

  return {
    token,
    hash: hashRefreshToken(token),
    expiresAt: new Date(
      Date.now() + REFRESH_TOKEN_DAYS * 24 * 60 * 60 * 1000,
    ),
  };
}

export function hashRefreshToken(token) {
  return crypto
    .createHash("sha256")
    .update(token)
    .digest("hex");
}
