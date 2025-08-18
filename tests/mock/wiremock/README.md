```sh
# --record-mappings is for the prox mode, remove it to act as a mock endpoint
docker run -it --rm \
  -p 2793:8080 \
  -v "$(pwd)/wiremock-recordings:/home/wiremock" \
  wiremock/wiremock:latest \
  --global-response-templating \
  --record-mappings
  #   add:   --verbose if needed
  ```

```sh
# only for proxy mode
# TARGET_API_URL: where to forward
# API_BEARER_TOKEN: token to use for the target API (secret)
docker run -it --rm \
  -p 2793:8080 \
  -v "$(pwd)/wiremock-recordings:/home/wiremock" \
  -e TARGET_API_URL="https://openrouter.ai/api" \
  -e API_BEARER_TOKEN="${{ secrets.YOUR_SECRET_TOKEN }}" \
  wiremock/wiremock:latest \
  --global-response-templating
  ```
2. second
3. third

