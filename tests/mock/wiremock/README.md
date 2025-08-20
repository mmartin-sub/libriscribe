
# WireMock Docker Commands

## 1. Proxy Mode with Recording

```sh
# --record-mappings is for the proxy mode, remove it to act as a mock endpoint
docker run -it --rm \
  -p 2793:8080 \
  -v "$(pwd)/wiremock-recordings:/home/wiremock" \
  wiremock/wiremock:latest \
  --global-response-templating \
  --record-mappings
  #   add:   --verbose if needed
```

## 2. Proxy Mode with Target Configuration

```sh
# only for proxy mode
# TARGET_API_URL: where to forward
# API_BEARER_TOKEN: token to use for the target API (secret)
docker run -it --rm \
  -p 2793:8080 \
  -v "$(pwd)/wiremock-recordings:/home/wiremock" \
  -e TARGET_API_URL="https://openrouter.ai/api" \
  -e API_BEARER_TOKEN="${{ secrets.YOUR_SECRET_TOKEN }}" \
  -e TARGET_HOST="${{ secrets.TARGET_HOST}}" \
  wiremock/wiremock:latest \
  --global-response-templating
```

## 3. Basic Mock Server

```sh
docker run -it --rm \
  -p 2793:8080 \
  -v "$(pwd)/wiremock-recordings:/home/wiremock" \
  wiremock/wiremock:latest \
  --global-response-templating
```

## 4. Mock Server with Different Mount Point

```sh
docker run -it --rm \
  -p 2793:8080 \
  -v "$(pwd)/wiremock-playing:/home/wiremock" \
  wiremock/wiremock:latest \
  --global-response-templating
```
