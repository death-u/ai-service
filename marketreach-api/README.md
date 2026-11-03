# MarketReach AI — Backend API

**Node.js | Express.js | MongoDB | JavaScript ES Modules**

MarketReach AI is an AI-powered retail distribution intelligence platform being developed by **SpellaHub Hackathon Team 2** for the **GBfoods Nigeria Hackathon 2026**.

This repository contains the backend REST API for authentication, retailer management, products, inventory, demand forecasting, analytics, and notifications.

**Organization:** Spella ICT Hub Limited (SpellaHub)  
**Project:** MarketReach AI  
**Architecture:** Feature-Based Modular Architecture  
**API Version:** v1  
**Status:** Active Development

---

## 1. Technology Stack

| Technology | Purpose |
|---|---|
| Node.js | Backend runtime |
| Express.js | REST API framework |
| MongoDB | NoSQL database |
| Mongoose | Database modeling |
| JavaScript ES Modules | Modern import/export syntax |
| Zod | Request and environment validation |
| bcryptjs | Password hashing |
| jsonwebtoken | JWT authentication |
| Helmet | HTTP security headers |
| CORS | Browser cross-origin configuration |
| express-rate-limit | API rate limiting |
| Pino | Application logging |
| Nodemon | Development server |
| Vitest | Automated testing |
| Supertest | HTTP endpoint testing |
| ESLint | Code quality |
| Prettier | Code formatting |

## 2. Prerequisites

Before working on the backend, install:

- Node.js 22 or a newer supported LTS release: https://nodejs.org
- Git: https://git-scm.com
- VS Code: https://code.visualstudio.com
- MongoDB Community Server or MongoDB Atlas: https://www.mongodb.com
- Postman: https://www.postman.com

Verify your installations:

```bash
node -v
npm -v
git --version
```

## 3. Clone the Repository

Clone the backend repository provided by the team lead:

```bash
git clone YOUR_BACKEND_REPOSITORY_URL
cd marketreach-backend
```

**Important:** Do not run `npm init` or generate a new Express project after cloning. The repository already contains the project configuration.

## 4. Install Dependencies

Run:

```bash
npm install
```

This installs all dependencies declared in `package.json`.

If the project is missing its dependencies during initial setup, the production dependencies are:

```bash
npm install express mongoose dotenv cors helmet compression express-rate-limit cookie-parser zod jsonwebtoken bcryptjs pino pino-http swagger-ui-express
```

Development dependencies:

```bash
npm install -D nodemon eslint @eslint/js globals prettier vitest supertest pino-pretty
```

Students cloning an existing repository should normally use only `npm install`, or `npm ci` when a valid committed `package-lock.json` is available.

## 5. Environment Configuration

Create a `.env` file in the project root by copying `.env.example`.

On Git Bash:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Example environment configuration:

```dotenv
NODE_ENV=development
PORT=5000
API_PREFIX=/api/v1

MONGODB_URI=mongodb://127.0.0.1:27017/marketreach_ai

JWT_ACCESS_SECRET=your-random-secret-at-least-32-characters
JWT_REFRESH_SECRET=another-random-secret-at-least-32-characters
JWT_ACCESS_EXPIRES_IN=15m
JWT_REFRESH_EXPIRES_IN=7d

CLIENT_URL=http://localhost:8081
LOG_LEVEL=debug
TRUST_PROXY=false
```

Generate strong secrets using:

```bash
node -e "console.log(require('node:crypto').randomBytes(48).toString('hex'))"
```

Run it twice and use different values for the two JWT secrets.

**Security rules:**

- Never commit `.env`.
- Never share passwords or JWT secrets in the group chat.
- Never hardcode database credentials.
- Never commit real customer data.
- Update `.env.example` when introducing a new environment variable, using placeholders rather than actual credentials.

## 6. MongoDB Setup

### Option A — Local MongoDB

Install MongoDB Community Server and start the MongoDB service.

Set:

```dotenv
MONGODB_URI=mongodb://127.0.0.1:27017/marketreach_ai
```

### Option B — MongoDB Atlas

1. Visit https://cloud.mongodb.com.
2. Create a project and database cluster.
3. Create a database user.
4. Configure appropriate network access.
5. Copy the MongoDB connection string.
6. Add it to your `.env` file.

Do not commit your Atlas connection string or allow unrestricted database access in production.

## 7. Run the Backend

Start the development server:

```bash
npm run dev
```

For normal execution:

```bash
npm start
```

Default local API address:

`http://localhost:5000`

Health endpoint:

`http://localhost:5000/api/v1/health`

Expected successful response:

```json
{
  "success": true,
  "message": "MarketReach AI API is healthy",
  "data": {
    "service": "marketreach-backend",
    "database": "connected",
    "uptime": 120,
    "timestamp": "2026-10-31T09:00:00.000Z"
  }
}
```

The timestamp and uptime will reflect the actual server state.

## 8. Official Project Folder Structure

All students must follow this structure.

```text
marketreach-backend/
│
├── src/
│   ├── app.js
│   ├── server.js
│   │
│   ├── config/
│   │   ├── env.js
│   │   ├── database.js
│   │   └── logger.js
│   │
│   ├── common/
│   │   ├── errors/
│   │   │   └── AppError.js
│   │   │
│   │   ├── middleware/
│   │   │   ├── authenticate.js
│   │   │   ├── authorize.js
│   │   │   ├── errorHandler.js
│   │   │   ├── notFound.js
│   │   │   └── validate.js
│   │   │
│   │   └── utils/
│   │       └── asyncHandler.js
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── controllers/
│   │   │   │   └── auth.controller.js
│   │   │   ├── services/
│   │   │   │   └── auth.service.js
│   │   │   ├── routes/
│   │   │   │   └── auth.routes.js
│   │   │   ├── schemas/
│   │   │   │   └── user.schema.js
│   │   │   ├── validations/
│   │   │   │   └── auth.validation.js
│   │   │   ├── types/
│   │   │   │   └── auth.types.js
│   │   │   ├── repositories/
│   │   │   │   └── auth.repository.js
│   │   │   ├── utils/
│   │   │   │   └── auth.tokens.js
│   │   │   └── index.js
│   │   │
│   │   ├── users/
│   │   ├── retailers/
│   │   ├── products/
│   │   ├── inventory/
│   │   ├── forecasts/
│   │   ├── insights/
│   │   └── notifications/
│   │
│   └── routes/
│       └── index.js
│
├── tests/
│   └── health.test.js
│
├── .env.example
├── .gitignore
├── .prettierrc.json
├── eslint.config.js
├── package.json
├── package-lock.json
└── README.md
```

Only the Auth and Health modules are implemented initially. Other module directories represent planned work.

## 9. Mandatory Module Architecture

Every business feature must follow the same pattern.

Example: Retailers module.

```text
src/modules/retailers/
├── controllers/
│   └── retailer.controller.js
├── services/
│   └── retailer.service.js
├── routes/
│   └── retailer.routes.js
├── schemas/
│   └── retailer.schema.js
├── validations/
│   └── retailer.validation.js
├── types/
│   └── retailer.types.js
├── repositories/
│   └── retailer.repository.js
├── utils/
└── index.js
```

### Responsibilities

| Folder | Responsibility |
|---|---|
| `controllers` | Handle requests and HTTP responses |
| `services` | Implement business logic |
| `routes` | Define endpoints and middleware |
| `schemas` | Define Mongoose models |
| `validations` | Define Zod validation rules |
| `types` | Define JSDoc data contracts and constants |
| `repositories` | Handle database queries |
| `utils` | Module-specific helper functions |
| `index.js` | Export the module's public interface |

The project uses JavaScript, not TypeScript. Therefore, the `types` folder contains JSDoc definitions and runtime constants.

## 10. Request Processing Flow

Every API request should follow this architecture:

```text
Client / Mobile Application
           |
           v
        API Route
           |
           v
  Authentication Middleware
           |
           v
    Request Validation
           |
           v
       Controller
           |
           v
        Service
           |
           v
       Repository
           |
           v
    Mongoose Schema
           |
           v
        MongoDB
```

The response flows back through the service and controller.

### Important Rules

**Routes:** Define URLs and middleware only. Do not write database queries in route files.

**Controllers:** Handle HTTP input and output. Do not put complex business logic in controllers.

**Services:** Handle business rules. Services should not depend on Express `req` or `res`.

**Repositories:** Perform database queries. Do not put HTTP responses inside repositories.

**Schemas:** Define database structure, indexes, defaults, and constraints.

**Validations:** Validate and normalize client input before business logic executes.

**Types:** Document shared data shapes using JSDoc.

## 11. ES Modules Standard

All files must use modern JavaScript ES Modules.

Correct:

```javascript
import express from "express";
import { authService } from "../services/auth.service.js";

export const example = () => {};
```

Avoid CommonJS:

```javascript
const express = require("express");
module.exports = {};
```

**Always include `.js` extensions in relative imports.**

## 12. API Response Standard

All endpoints must return a consistent JSON structure.

### Successful Response

```json
{
  "success": true,
  "message": "Retailer created successfully",
  "data": {
    "id": "example-id",
    "businessName": "Sample Retail Store"
  }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Request validation failed",
  "errors": [
    {
      "field": "body.businessName",
      "message": "Business name is required"
    }
  ]
}
```

### HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 204 | Successful request with no response body |
| 400 | Invalid request |
| 401 | Authentication required or invalid |
| 403 | Access forbidden |
| 404 | Resource not found |
| 409 | Resource conflict |
| 429 | Too many requests |
| 500 | Internal server error |
| 503 | Service unavailable |

## 13. Authentication Module

The Auth module serves as the reference implementation for the entire backend.

### Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Log in |
| POST | `/api/v1/auth/refresh` | Refresh tokens |
| POST | `/api/v1/auth/logout` | Revoke refresh token |
| GET | `/api/v1/auth/me` | Retrieve authenticated user |

### User Roles

- `ADMIN`
- `DISTRIBUTOR`
- `FIELD_AGENT`

Public registration creates a `DISTRIBUTOR` account. Users cannot assign themselves privileged roles.

Protected endpoints use JWT access tokens.

Example:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

The mobile application must store tokens securely. Never log or expose passwords, password hashes, or refresh tokens.

## 14. Module Naming Conventions

All students must use consistent naming.

| Item | Example |
|---|---|
| Folder | `retailers` |
| Controller | `retailer.controller.js` |
| Service | `retailer.service.js` |
| Repository | `retailer.repository.js` |
| Route | `retailer.routes.js` |
| Schema | `retailer.schema.js` |
| Validation | `retailer.validation.js` |
| Types | `retailer.types.js` |
| Module entry | `index.js` |

Use camelCase for variables and functions, PascalCase for classes and Mongoose model names, and UPPER_SNAKE_CASE for constants.

Use descriptive function names such as `createRetailer`, `findRetailerById`, and `updateInventory`.

## 15. Backend Modules and Responsibilities

| Module | Main Features |
|---|---|
| Auth | Registration, login, JWT, logout |
| Users | User profiles, roles, team members |
| Retailers | Registration, profiles, locations, search |
| Products | Products, categories, pricing |
| Inventory | Stock quantities, stock movements, alerts |
| Forecasts | Demand predictions, forecast records |
| Insights | Dashboard metrics, trends, recommendations |
| Notifications | Low-stock and operational alerts |

All business data must be scoped to the correct organization or distributor. Authentication alone does not authorize access to another organization's records.

## 16. GitHub Collaboration

Every student must work on a separate feature branch.

### Update Your Local Repository

```bash
git switch main
git pull origin main
```

### Create a Feature Branch

```bash
git switch -c feature/retailer-module
```

### Commit Your Work

```bash
git add .
git commit -m "feat(retailers): implement retailer registration"
```

### Push to GitHub

```bash
git push -u origin feature/retailer-module
```

Open a Pull Request to merge into `main`.

### Commit Message Format

```text
type(scope): short description
```

Examples:

```text
feat(auth): implement user registration
feat(retailers): add retailer CRUD endpoints
feat(inventory): implement stock movement tracking
fix(auth): handle invalid refresh tokens
refactor(retailers): move queries into repository
test(auth): add login integration tests
docs(api): update endpoint documentation
chore(config): configure environment validation
```

**Do not push directly to `main` unless authorized by the team lead.**

## 17. Pull Request Requirements

Before opening a Pull Request:

- [ ] Code follows the module structure.
- [ ] Business logic is inside services.
- [ ] Database queries are inside repositories.
- [ ] Input validation is implemented.
- [ ] Protected routes use appropriate authorization.
- [ ] Organization ownership checks are implemented where required.
- [ ] API responses follow the standard format.
- [ ] Errors are handled centrally.
- [ ] Tests pass.
- [ ] ESLint passes.
- [ ] No secrets are committed.
- [ ] The feature has been tested using Postman or automated tests.
- [ ] The Pull Request describes the changes and testing performed.

## 18. Development Commands

| Command | Description |
|---|---|
| `npm install` | Install dependencies |
| `npm run dev` | Start development server |
| `npm start` | Start application |
| `npm test` | Run automated tests |
| `npm run test:watch` | Run tests in watch mode |
| `npm run lint` | Check code quality |
| `npm run format` | Format code |
| `npm run format:check` | Verify formatting |

## 19. Testing Standards

Each module must be tested before merging.

At minimum, test:

- Successful operations.
- Missing required fields.
- Invalid data formats.
- Duplicate records.
- Unauthorized requests.
- Forbidden access.
- Nonexistent resources.
- Database error handling.
- Cross-organization access restrictions.

For authentication, also test password hashing, invalid credentials, token expiry, refresh-token rotation, and logout.

Automated tests should use a separate test database or properly mocked database dependencies. Never run destructive tests against production data.

## 20. API Documentation

The team will maintain API documentation using Swagger/OpenAPI.

Every implemented endpoint should document:

- HTTP method and URL.
- Authentication requirements.
- Request body and parameters.
- Validation rules.
- Success response.
- Error responses.
- Example payloads.

Swagger UI will be enabled once the OpenAPI specification and documentation route are configured.

Until then, developers should share Postman requests and keep endpoint contracts documented in their Pull Requests.

## 21. Security Guidelines

All backend developers must follow these rules:

1. Hash passwords before storing them.
2. Never return password hashes.
3. Validate all incoming data.
4. Authenticate protected endpoints.
5. Enforce role and resource ownership permissions.
6. Never trust IDs supplied by the frontend without checking access.
7. Never expose environment secrets.
8. Avoid logging sensitive credentials.
9. Apply rate limiting to sensitive endpoints.
10. Use HTTPS in deployed environments.
11. Keep dependencies updated.
12. Do not use real retailer data without authorization.

## 22. Troubleshooting

### MongoDB Connection Failed

Check that MongoDB is running and that `MONGODB_URI` is correct.

### Missing Environment Variable

Check `.env` against `.env.example` and restart the server.

### Module Not Found

Run:

```bash
npm install
```

Check relative import paths and `.js` extensions.

### Port Already in Use

Stop the process using port 5000 or change `PORT` in `.env`.

### JWT Verification Failed

Check that the token is valid, has not expired, and was signed using the configured secret.

### Server Crashes After Adding a Module

Check that every imported file exists, every module exports the expected values, and its route has been registered correctly.

## 23. Development Roadmap

- [x] Initialize Node.js and Express.
- [x] Configure ES Modules.
- [x] Set up MongoDB connection.
- [x] Configure environment validation.
- [x] Implement shared middleware.
- [x] Establish modular architecture.
- [x] Prepare Auth module implementation.
- [ ] Complete Auth module testing.
- [ ] Implement Users module.
- [ ] Implement Retailers module.
- [ ] Implement Products module.
- [ ] Implement Inventory module.
- [ ] Implement Demand Forecasts.
- [ ] Implement Insights and Analytics.
- [ ] Implement Notifications.
- [ ] Complete API documentation.
- [ ] Integrate mobile application.
- [ ] Deploy backend.
- [ ] Complete hackathon testing.

## 24. Instructions to All Backend Students

**The Auth module is our reference architecture.**

Before building any new module, study how Auth separates controllers, services, repositories, schemas, validations, routes, and types.

Every student must:

- Follow the official folder structure.
- Use JavaScript ES Modules.
- Keep each feature independent and modular.
- Write readable and maintainable code.
- Follow the shared API response conventions.
- Create a separate GitHub branch.
- Test work before submitting it.
- Submit a Pull Request for review.
- Communicate API changes to the frontend team.

**Our goal is not just to make the hackathon application work. We are building a backend that can be maintained, extended, and deployed beyond the competition.**

---

**MarketReach AI — Backend Engineering Team**

*Built by SpellaHub Hackathon Team 2.*

*Powered by Spella ICT Hub Limited.*