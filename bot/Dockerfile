# syntax=docker/dockerfile:1

FROM node:18-alpine AS builder
WORKDIR /usr/src/app

COPY . .
RUN npm ci && npm run build

FROM node:18-alpine AS base
WORKDIR /usr/src/app
ENV NODE_ENV=production

COPY package.json package-lock.json ./
RUN npm ci

COPY --from=builder /usr/src/app/dist ./dist

CMD ["npm", "start"]
EXPOSE 8080
