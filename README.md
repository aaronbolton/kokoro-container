# Docker Quickstart 

```bash
docker run \
  --name kokoro-tts \
  -p 5001:5001 \
  -v $(pwd)/kokoro-tts/output:/app/output \
  -v $(pwd)/kokoro-tts/input:/app/input \
  -v $(pwd)/kokoro-tts/huggingface:/root/.cache/huggingface \
  --gpus all \
  aaronbolton78/kokoro-container:latest
```
or use the provided `docker-compose.yml`
