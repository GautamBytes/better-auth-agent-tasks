import { describe, expect, it } from "vitest";
import { wildcardMatch } from "./wildcard";

const cases = [
	{
		name: "global",
		pattern: "*.txt",
		options: { flags: "g" },
		sample: "readme.txt",
		miss: "readme.md",
	},
	{
		name: "sticky",
		pattern: "*.txt",
		options: { flags: "y" },
		sample: "readme.txt",
		miss: "readme.md",
	},
	{
		name: "global and case insensitive",
		pattern: "*.txt",
		options: { flags: "gi" },
		sample: "README.TXT",
		miss: "readme.md",
	},
	{
		name: "sticky and case insensitive",
		pattern: "*.txt",
		options: { flags: "iy" },
		sample: "README.TXT",
		miss: "readme.md",
	},
	{
		name: "pattern array",
		pattern: ["src/*.ts", "test/*.ts"],
		options: { flags: "g" },
		sample: "src/app.ts",
		miss: "docs/app.md",
	},
	{
		name: "custom separator",
		pattern: "*.example.com",
		options: { flags: "y", separator: "." },
		sample: "app.example.com",
		miss: "deep.app.example.com",
	},
];

describe("wildcard matcher call stability", () => {
	it.each(cases)(
		"keeps $name matching independent of earlier calls",
		({ pattern, options, sample, miss }) => {
			const match = wildcardMatch(pattern, options);
			expect(match(sample)).toBe(true);
			expect(match(sample)).toBe(true);
			expect(match(miss)).toBe(false);
			expect(match(sample)).toBe(true);
			expect(match(miss)).toBe(false);
			expect(match(sample)).toBe(true);
			expect(match.pattern).toEqual(pattern);
			expect(match.options).toEqual(options);
			expect(match.regexp.flags).toBe(options.flags);
			// @ts-expect-error Exercise invalid JavaScript input at the runtime boundary.
			expect(() => match(42)).toThrow(TypeError);
		},
	);
});
