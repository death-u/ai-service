
import { asyncHandler } from "../../../common/utils/asyncHandler.js";
import { authService } from "../services/auth.service.js";

export const register = asyncHandler(async (req, res) => {
  const data = await authService.register(req.validated.body);

  res.status(201).json({
    success: true,
    message: "Account created successfully",
    data,
  });
});

export const login = asyncHandler(async (req, res) => {
  const data = await authService.login(req.validated.body);

  res.status(200).json({
    success: true,
    message: "Login successful",
    data,
  });
});

export const refresh = asyncHandler(async (req, res) => {
  const data = await authService.refresh(
    req.validated.body.refreshToken,
  );

  res.status(200).json({
    success: true,
    message: "Tokens refreshed successfully",
    data,
  });
});

export const logout = asyncHandler(async (req, res) => {
  await authService.logout(req.validated.body.refreshToken);

  res.status(200).json({
    success: true,
    message: "Logged out successfully",
  });
});

export const me = asyncHandler(async (req, res) => {
  const user = await authService.me(req.user.id);

  res.status(200).json({
    success: true,
    message: "Profile retrieved successfully",
    data: user,
  });
});
