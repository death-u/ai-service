
import bcrypt from "bcryptjs";
import mongoose from "mongoose";

import { AppError } from "../../../common/errors/AppError.js";
import { authRepository } from "../repositories/auth.repository.js";
import { PUBLIC_REGISTRATION_ROLE } from "../types/auth.types.js";
import {
  createAccessToken,
  createRefreshToken,
  hashRefreshToken,
} from "../utils/auth.tokens.js";

function publicUser(user) {
  return {
    id: user._id.toString(),
    fullName: user.fullName,
    email: user.email,
    role: user.role,
    isActive: user.isActive,
  };
}

function authResponse(user, refreshToken) {
  return {
    user: publicUser(user),
    tokens: {
      accessToken: createAccessToken(user),
      refreshToken,
      tokenType: "Bearer",
    },
  };
}

export const authService = {
  async register({ fullName, email, password }) {
    const existingUser = await authRepository.findByEmail(email);

    if (existingUser) {
      throw new AppError("Email is already registered", 409);
    }

    const passwordHash = await bcrypt.hash(password, 12);

    let user;

    try {
      user = await authRepository.create({
        fullName,
        email,
        passwordHash,
        role: PUBLIC_REGISTRATION_ROLE,
      });
    } catch (error) {
      if (error.code === 11000) {
        throw new AppError("Email is already registered", 409);
      }

      throw error;
    }

    const refresh = createRefreshToken();

    await authRepository.saveSession(
      user._id,
      refresh.hash,
      refresh.expiresAt,
    );

    return authResponse(user, refresh.token);
  },

  async login({ email, password }) {
    const user = await authRepository.findByEmail(email);

    if (!user) {
      throw new AppError("Invalid email or password", 401);
    }

    const passwordMatches = await bcrypt.compare(
      password,
      user.passwordHash,
    );

    if (!passwordMatches) {
      throw new AppError("Invalid email or password", 401);
    }

    if (!user.isActive) {
      throw new AppError("Account is disabled", 403);
    }

    const refresh = createRefreshToken();

    await authRepository.saveSession(
      user._id,
      refresh.hash,
      refresh.expiresAt,
    );

    return authResponse(user, refresh.token);
  },

  async refresh(refreshToken) {
    const oldHash = hashRefreshToken(refreshToken);

    const user = await authRepository.findByIdWithSession(
      await findSessionUserId(oldHash),
    );

    if (!user || !user.isActive) {
      throw new AppError("Invalid or expired refresh token", 401);
    }

    const nextRefresh = createRefreshToken();

    const updatedUser = await authRepository.rotateSession(
      user._id,
      oldHash,
      nextRefresh.hash,
      nextRefresh.expiresAt,
    );

    if (!updatedUser) {
      throw new AppError("Invalid or expired refresh token", 401);
    }

    return authResponse(updatedUser, nextRefresh.token);
  },

  async logout(refreshToken) {
    const tokenHash = hashRefreshToken(refreshToken);
    const userId = await findSessionUserId(tokenHash);

    if (userId) {
      await authRepository.revokeSession(userId, tokenHash);
    }

    return { message: "Logged out successfully" };
  },

  async me(userId) {
    if (!mongoose.isValidObjectId(userId)) {
      throw new AppError("Invalid user identifier", 401);
    }

    const user = await authRepository.findById(userId);

    if (!user || !user.isActive) {
      throw new AppError("User not found or inactive", 401);
    }

    return publicUser(user);
  },
};

async function findSessionUserId(tokenHash) {
  const { User } = await import("../schemas/user.schema.js");

  const user = await User.findOne({
    refreshTokenHash: tokenHash,
    refreshTokenExpiresAt: { $gt: new Date() },
    isActive: true,
  }).select("_id");

  return user?._id ?? null;
}
