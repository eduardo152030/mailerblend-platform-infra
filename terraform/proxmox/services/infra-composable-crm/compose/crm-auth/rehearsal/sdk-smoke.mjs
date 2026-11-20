import assert from "node:assert/strict";
import { createHmac, randomBytes } from "node:crypto";
import { readFileSync } from "node:fs";
import { isIP } from "node:net";
import { setTimeout } from "node:timers/promises";
import { createClient } from "@supabase/supabase-js";

const host = process.argv[2];
assert.equal(isIP(host), 4);
assert.match(host, /^(10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.)/);
const config = Object.fromEntries(readFileSync(0, "utf8").trim().split("\n").map(line => line.split("=")));
const base = "http://" + host + ":9999";
function token(role) {
  const prefix = [
    { alg: "HS256", typ: "JWT" },
    { role, exp: Math.floor(Date.now() / 1000) + 300 },
  ].map(value => Buffer.from(JSON.stringify(value)).toString("base64url")).join(".");
  return prefix + "." + createHmac("sha256", config.CRM_REHEARSAL_JWT_SECRET).update(prefix).digest("base64url");
}
function client(role) {
  return createClient(base, token(role), {
    auth: { autoRefreshToken: false, persistSession: false, detectSessionInUrl: false },
    global: { fetch: (url, init) => fetch(url.replace(base + "/auth/v1", base), init) },
  });
}
const admin = client("service_role");
const browser = client("anon");
const email = "sdk." + randomBytes(8).toString("hex") + "@example.com";
const password = randomBytes(24).toString("hex");
const roles = { linkedin_sourcing: "editor" };
const created = await admin.auth.admin.createUser({
  email, password, email_confirm: true, app_metadata: { project_roles: roles },
});
assert.ok(!created.error, "Synthetic admin account creation");
const login = await browser.auth.signInWithPassword({ email, password });
assert.ok(!login.error, "Supabase JS login");
assert.deepEqual(login.data.user.app_metadata.project_roles, roles);
const renewed = await browser.auth.refreshSession();
assert.ok(!renewed.error, "Supabase JS refresh");
const session = renewed.data.session;
const logout = await browser.auth.signOut();
assert.ok(!logout.error, "Supabase JS logout");
const revoked = await client("anon").auth.refreshSession({ refresh_token: session.refresh_token });
assert.ok(revoked.error, "Revoked refresh token rejected");
const delay = Math.max(0, session.expires_at * 1000 - Date.now()) + 1500;
await setTimeout(delay);
const expired = await client("anon").auth.getUser(session.access_token);
assert.ok(expired.error, "Expired access token rejected");
console.log("Supabase JS PASS: admin, login, refresh, logout, refresh revocado y acceso expirado");
