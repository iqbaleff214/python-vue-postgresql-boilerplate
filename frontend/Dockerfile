# Build stage
FROM node:22.5.1-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_APP_NAME
ARG VITE_APP_API_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_API_URL=$VITE_APP_API_URL

RUN npm run build

# Runtime stage
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
