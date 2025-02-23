ARG LANG_VERSION

FROM node:$LANG_VERSION-slim

ARG FUNCTION_DEPENDENCIES

WORKDIR /app

COPY package*.json ./

ARG FUNCTION_DEPENDENCIES

RUN if [ -n "${FUNCTION_DEPENDENCIES}" ]; then npm install ${FUNCTION_DEPENDENCIES}; fi

RUN npm install

COPY . .

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD curl -f http://localhost:8001/ || exit 1

EXPOSE 8001

CMD ["npm", "start"]