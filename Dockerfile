FROM node:20-bullseye AS web-builder
WORKDIR /app/apps/web
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm install
COPY apps/web .
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx nodejs npm curl gettext-base \
  && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt /app/apps/api/requirements.txt
RUN pip install --no-cache-dir -r /app/apps/api/requirements.txt

COPY apps/api /app/apps/api
COPY --from=web-builder /app/apps/web/.next/standalone /app/apps/web/.next/standalone
COPY --from=web-builder /app/apps/web/.next/static /app/apps/web/.next/static
COPY --from=web-builder /app/apps/web/public /app/apps/web/public
COPY nginx/nginx.conf.template /app/nginx/nginx.conf.template
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

ENV PORT=8080
ENV PYTHONPATH=/app/apps/api

EXPOSE 8080

CMD ["/app/start.sh"]
