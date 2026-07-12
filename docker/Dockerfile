ARG ESPHOME_VERSION=2026.6
FROM ghcr.io/esphome/esphome:${ESPHOME_VERSION}

WORKDIR /workspace

# Keep the image useful both interactively and in CI. All compilers and Python
# dependencies remain inside this container and its Docker volumes.
ENTRYPOINT ["esphome"]
CMD ["version"]

