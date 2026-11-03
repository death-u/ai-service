
import { Router } from "express";

import { validate } from "../../../common/middleware/validate.js";
import { authenticate } from "../../../common/middleware/authenticate.js";

import {
  register,
  login,
  refresh,
  logout,
  me,
} from "../controllers/auth.controller.js";

import {
  registerValidation,
  loginValidation,
  refreshValidation,
} from "../validations/auth.validation.js";

const router = Router();

router.post(
  "/register",
  validate(registerValidation),
  register,
);

router.post(
  "/login",
  validate(loginValidation),
  login,
);

router.post(
  "/refresh",
  validate(refreshValidation),
  refresh,
);

router.post(
  "/logout",
  validate(refreshValidation),
  logout,
);

router.get("/me", authenticate, me);

export default router;
