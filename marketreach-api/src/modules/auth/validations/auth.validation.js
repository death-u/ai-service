
import { z } from "zod";

const email = z
  .string()
  .trim()
  .email("Enter a valid email address")
  .max(254)
  .transform((value) => value.toLowerCase());

const password = z
  .string()
  .min(8, "Password must contain at least 8 characters")
  .max(128, "Password must not exceed 128 characters");

export const registerValidation = z.object({
  body: z
    .object({
      fullName: z.string().trim().min(2).max(100),
      email,
      password,
    })
    .strict(),
});

export const loginValidation = z.object({
  body: z
    .object({
      email,
      password: z.string().min(1),
    })
    .strict(),
});

export const refreshValidation = z.object({
  body: z
    .object({
      refreshToken: z.string().min(1),
    })
    .strict(),
});
