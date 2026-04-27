FROM nginx:1.27-alpine

ARG TENANT_DIR

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ${TENANT_DIR}/index.html /usr/share/nginx/html/index.html
