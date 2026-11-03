
import { Router } from "express";

import healthRoutes from "../modules/health/health.routes.js";
import { authRoutes } from "../modules/auth/index.js";

const router = Router();

router.use("/health", healthRoutes);
router.use("/auth", authRoutes);

// Future business modules:
//
// router.use("/users", userRoutes);
// router.use("/retailers", retailerRoutes);
// router.use("/products", productRoutes);
// router.use("/inventory", inventoryRoutes);
// router.use("/forecasts", forecastRoutes);
// router.use("/insights", insightRoutes);
// router.use("/notifications", notificationRoutes);

export default router;
