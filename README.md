

```bash
docker run \
  --name kokoro-tts \
  -p 5001:5001 \
  -v $(pwd)/kokoro-tts/output:/app/output \
  -v $(pwd)/kokoro-tts/input:/app/input \
  --network private_network \
  --gpus '"device=0,1"' \
  aaronbolton78/kokoro-container:latest
```

