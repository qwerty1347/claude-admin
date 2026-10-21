# Next 공식 Docker 예시(standalone 출력) 구조. stage: dev / build / prod
FROM node:24-slim AS base
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# 개발: compose.override.yaml 에서 소스를 마운트하고 next dev 로 실행
FROM deps AS dev
COPY . .
CMD ["npm", "run", "dev"]

# 빌드
FROM deps AS build
COPY . .
RUN npm run build

# 배포: 빌드 결과만, 일반 사용자로 실행
FROM base AS prod
ENV NODE_ENV=production PORT=3001 HOSTNAME=0.0.0.0
COPY --from=build /app/public ./public
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
USER node
CMD ["node", "server.js"]
