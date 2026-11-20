FROM node:22.14.0-alpine@sha256:9bef0ef1e268f60627da9ba7d7605e8831d5b56ad07487d24d1aa386336d1944 AS build
WORKDIR /app
COPY crm-core-main/package.json crm-core-main/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY crm-core-main/ ./
ARG VITE_CRM_AUTH_ANON_KEY
RUN npm run build

FROM nginx:1.28.0-alpine@sha256:30f1c0d78e0ad60901648be663a710bdadf19e4c10ac6782c235200619158284
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/ /usr/share/nginx/html/
