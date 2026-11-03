
/**
 * MarketReach AI authentication contracts.
 *
 * @typedef {"ADMIN" | "DISTRIBUTOR" | "FIELD_AGENT"} UserRole
 */

/**
 * @typedef {Object} PublicUser
 * @property {string} id
 * @property {string} fullName
 * @property {string} email
 * @property {UserRole} role
 * @property {boolean} isActive
 */

/**
 * @typedef {Object} AuthTokens
 * @property {string} accessToken
 * @property {string} refreshToken
 * @property {string} tokenType
 */

/**
 * @typedef {Object} AuthResult
 * @property {PublicUser} user
 * @property {AuthTokens} tokens
 */

export const USER_ROLES = Object.freeze({
  ADMIN: "ADMIN",
  DISTRIBUTOR: "DISTRIBUTOR",
  FIELD_AGENT: "FIELD_AGENT",
});

export const PUBLIC_REGISTRATION_ROLE = USER_ROLES.DISTRIBUTOR;
