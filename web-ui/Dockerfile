# Web UI: build with node, serve with unprivileged nginx on 8080 (OpenShift restricted policy).
ARG NODE_IMAGE=node:22
ARG NGINX_IMAGE=nginxinc/nginx-unprivileged:stable

FROM ${NODE_IMAGE} AS build
ARG NPM_REGISTRY=""
WORKDIR /src
COPY package.json package-lock.json ./
RUN if [ -n "$NPM_REGISTRY" ]; then npm config set registry "$NPM_REGISTRY"; fi && npm ci
COPY index.html tsconfig.json vite.config.ts ./
COPY src ./src
RUN npm run build

FROM ${NGINX_IMAGE}
COPY --from=build /src/dist /usr/share/nginx/html
# Rendered by the image's envsubst templating; set ICEOBS_UI_BACKEND_URL at runtime.
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 8080
