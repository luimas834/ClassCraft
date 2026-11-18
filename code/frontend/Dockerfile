# The frontend image. Only the development stage exists so far; the production
# stage that serves the built files is added with the production stack.
FROM node:24-alpine AS dev

WORKDIR /app

# Install the packages on their own layer, so a code change does not repeat it.
COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
