import { wildcardMatch } from "/app/packages/better-auth/src/utils/wildcard.ts";
for (const flags of ["g", "y"]) {
 const matches = wildcardMatch("*.txt", { flags });
 console.log(`${flags}: ${[matches("readme.txt"), matches("readme.txt"), matches("readme.txt")].join(" ")}`);
}
