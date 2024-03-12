# Use a base image
FROM scratch

ENV WASMEDGE_PLUGIN_PATH=${WASMEDGE_PLUGIN_PATH:-"/usr/lib/wasmedge"}
ENV WASMEDGE_WASINN_PRELOAD=${WASMEDGE_WASINN_PRELOAD:-"default:GGML:AUTO:model.gguf"}

WORKDIR /app

# Copy wasm files to the directory
COPY llama-chat.wasm /app

# COPY model.gguf /app
ENTRYPOINT ["/app/llama-chat.wasm"]