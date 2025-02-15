ARG PY_VERSION

FROM python:$PY_VERSION-slim

ARG FUNCTION_DEPENDENCIES

WORKDIR /app
COPY . .

RUN if [ -n "${FUNCTION_DEPENDENCIES}" ]; then pip install ${FUNCTION_DEPENDENCIES}; fi
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
