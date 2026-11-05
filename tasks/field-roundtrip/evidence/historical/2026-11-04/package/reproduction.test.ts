import type { BetterAuthOptions } from "@better-auth/core";
import type { SecondaryStorage } from "@better-auth/core/db";
import { describe, expect, it } from "vitest";
import { jwt } from "../../plugins/jwt";
import { getTestInstance } from "../../test-utils/test-instance";

type CookieStrategy = NonNullable<
	NonNullable<
		NonNullable<BetterAuthOptions["session"]>["cookieCache"]
	>["strategy"]
>;
type StorageRoute =
	| { kind: "cookie"; strategy: CookieStrategy }
	| { kind: "secondary"; parsed: boolean }
	| { kind: "database" }
	| { kind: "jwt-plugin" };

const timestampStrings = [
	"2024-01-02T03:04:05Z",
	"2031-09-08T07:06:05.123400Z",
];
const cookieStrategies = ["compact", "jwt", "jwe"] satisfies CookieStrategy[];

function jsonValue(value: string) {
	return {
		createdAt: value,
		nested: { expiresAt: value, enabled: true, count: 7, missing: null },
		items: [value, "ordinary text", null, { updatedAt: value }],
		empty: [],
	};
}

function fieldOptions(value: string) {
	return {
		user: {
			additionalFields: {
				trackingId: { type: "string", required: false },
				aliases: { type: "string[]", required: false },
				preferences: { type: "json", required: false },
				joinedOn: { type: "date", required: false },
				optionalText: { type: "string", required: false },
				emptyTags: { type: "string[]", required: false },
				secretAuditNote: {
					type: "string",
					input: false,
					returned: false,
					defaultValue: "private note",
				},
			},
		},
		session: {
			additionalFields: {
				cursor: { type: "string", defaultValue: value },
				history: { type: "string[]", defaultValue: [value, "plain"] },
				data: { type: "json", defaultValue: jsonValue(value) },
				reviewDate: { type: "date", defaultValue: new Date(value) },
				nullableText: { type: "string", required: false, defaultValue: null },
				emptyHistory: { type: "string[]", defaultValue: [] },
			},
		},
	} satisfies BetterAuthOptions;
}

function secondaryStorage(parsed: boolean): SecondaryStorage {
	const values = new Map<string, string>();
	function read(key: string): unknown {
		const value = values.get(key);
		return value === undefined ? null : parsed ? JSON.parse(value) : value;
	}
	return {
		get: read,
		getAndDelete(key) {
			const value = read(key);
			values.delete(key);
			return value;
		},
		increment(key) {
			const count = Number(values.get(key) ?? 0) + 1;
			values.set(key, String(count));
			return count;
		},
		set(key, value) {
			values.set(key, value);
		},
		delete(key) {
			values.delete(key);
		},
	};
}

function requestCookies(headers: Headers) {
	return new Headers({
		cookie: headers
			.getSetCookie()
			.map((cookie) => cookie.split(";")[0])
			.join("; "),
	});
}

function expectUser(user: unknown, value: string) {
	expect.soft(user).toMatchObject({
		trackingId: value,
		aliases: [value, "plain"],
		preferences: jsonValue(value),
		joinedOn: new Date(value),
		optionalText: null,
		emptyTags: [],
		createdAt: expect.any(Date),
		updatedAt: expect.any(Date),
	});
	expect.soft(user).not.toHaveProperty("secretAuditNote");
}

function expectSession(session: unknown, value: string) {
	expect.soft(session).toMatchObject({
		cursor: value,
		history: [value, "plain"],
		data: jsonValue(value),
		reviewDate: new Date(value),
		nullableText: null,
		emptyHistory: [],
		createdAt: expect.any(Date),
		updatedAt: expect.any(Date),
		expiresAt: expect.any(Date),
	});
}

async function expectStorageRoundTrip(value: string, route: StorageRoute) {
	const fields = fieldOptions(value);
	const { auth } = await getTestInstance(
		{
			...fields,
			logger: { disabled: true },
			plugins:
				route.kind === "jwt-plugin" ? [jwt({ sessionCookieCache: true })] : [],
			secondaryStorage:
				route.kind === "secondary" ? secondaryStorage(route.parsed) : undefined,
			session: {
				...fields.session,
				cookieCache: {
					enabled: route.kind === "cookie" || route.kind === "jwt-plugin",
					strategy:
						route.kind === "jwt-plugin"
							? "jwt"
							: route.kind === "cookie"
								? route.strategy
								: "compact",
				},
			},
		},
		{ disableTestUser: true },
	);
	const signup = await auth.api.signUpEmail({
		body: {
			email: "roundtrip@example.com",
			name: "Roundtrip",
			password: "password123",
			trackingId: value,
			aliases: [value, "plain"],
			preferences: jsonValue(value),
			joinedOn: new Date(value),
			optionalText: null,
			emptyTags: [],
		},
		returnHeaders: true,
	});
	expectUser(signup.response.user, value);
	const headers = requestCookies(signup.headers);
	if (route.kind === "cookie" || route.kind === "jwt-plugin") {
		const backing = await auth.api.getSession({
			headers,
			query: { disableCookieCache: true },
		});
		expect(backing).not.toBeNull();
		expect.soft(backing?.user.trackingId).toBe(value);
	}
	const restored = await auth.api.getSession({ headers });
	expect(restored).not.toBeNull();
	expectUser(restored?.user, value);
	expectSession(restored?.session, value);
	if (route.kind === "secondary") {
		await auth.api.updateUser({ headers, body: { name: "Renamed" } });
		const afterUserUpdate = await auth.api.getSession({ headers });
		expectUser(afterUserUpdate?.user, value);
		expectSession(afterUserUpdate?.session, value);
		await auth.api.updateSession({ headers, body: { cursor: value } });
		const afterSessionUpdate = await auth.api.getSession({ headers });
		expectUser(afterSessionUpdate?.user, value);
		expectSession(afterSessionUpdate?.session, value);
	}
}

/**
 * @see https://github.com/better-auth/better-auth/blob/e7200d132f5946490c19a389b5a89b31aeead4e7/packages/core/src/db/type.ts
 * @see https://github.com/better-auth/better-auth/pull/4237
 */
describe.each(timestampStrings)(
	"additional-field round trips for %s",
	(value) => {
		it.each(cookieStrategies)(
			"preserves field types through the %s cookie cache",
			async (strategy) => {
				await expectStorageRoundTrip(value, { kind: "cookie", strategy });
			},
		);

		it("preserves field types through JWT-plugin cookie signing", async () => {
			await expectStorageRoundTrip(value, { kind: "jwt-plugin" });
		});

		it("preserves field types through JSON-string secondary storage", async () => {
			await expectStorageRoundTrip(value, { kind: "secondary", parsed: false });
		});

		it("preserves field types through pre-parsed secondary storage", async () => {
			await expectStorageRoundTrip(value, { kind: "secondary", parsed: true });
		});

		it("preserves field types through SQLite array and JSON serialization", async () => {
			await expectStorageRoundTrip(value, { kind: "database" });
		});
	},
);
