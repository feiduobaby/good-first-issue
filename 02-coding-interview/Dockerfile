# Lightweight Node image
FROM node:22-alpine AS base
WORKDIR /usr/src/app

# Install production deps
COPY package.json package-lock.json* ./
RUN npm install --production

# Copy app source
COPY . .

ENV NODE_ENV=production \
    PORT=3000

EXPOSE 3000

CMD ["npm", "start"]

