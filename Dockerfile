FROM node:24.19.0-bookworm-slim@sha256:a9f5f7c91a432850b2a8a7797adf5eadb6c733ceed61167806cee7ea7fbc29df
ENV COREPACK_HOME=/opt/corepack CI=true DO_NOT_TRACK=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends git=1:2.39.5-0+deb12u3 python3=3.11.2-1+b1 ca-certificates=20250419~deb12u2 \
 && rm -rf /var/lib/apt/lists/* \
 && corepack enable \
 && corepack prepare pnpm@11.1.1 --activate
WORKDIR /app
COPY . .
RUN mkdir -p /pnpm/store \
 && chown -R node:node /app /pnpm
USER node
RUN pnpm install --frozen-lockfile --filter better-auth... --ignore-scripts --store-dir /pnpm/store
RUN pnpm --filter 'better-auth^...' build
CMD ["/bin/bash"]
