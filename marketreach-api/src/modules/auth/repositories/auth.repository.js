
import { User } from "../schemas/user.schema.js";

export const authRepository = {
  findByEmail(email) {
    return User.findOne({ email }).select(
      "+passwordHash +refreshTokenHash +refreshTokenExpiresAt",
    );
  },

  findById(id) {
    return User.findById(id);
  },

  findByIdWithSession(id) {
    return User.findById(id).select(
      "+refreshTokenHash +refreshTokenExpiresAt",
    );
  },

  create(data) {
    return User.create(data);
  },

  async saveSession(userId, tokenHash, expiresAt) {
    return User.findByIdAndUpdate(
      userId,
      {
        $set: {
          refreshTokenHash: tokenHash,
          refreshTokenExpiresAt: expiresAt,
          lastLoginAt: new Date(),
        },
      },
      { new: true },
    );
  },

  rotateSession(userId, oldHash, newHash, expiresAt) {
    return User.findOneAndUpdate(
      {
        _id: userId,
        isActive: true,
        refreshTokenHash: oldHash,
        refreshTokenExpiresAt: { $gt: new Date() },
      },
      {
        $set: {
          refreshTokenHash: newHash,
          refreshTokenExpiresAt: expiresAt,
        },
      },
      { new: true },
    );
  },

  revokeSession(userId, tokenHash) {
    return User.findOneAndUpdate(
      {
        _id: userId,
        refreshTokenHash: tokenHash,
      },
      {
        $set: {
          refreshTokenHash: null,
          refreshTokenExpiresAt: null,
        },
      },
    );
  },
};
