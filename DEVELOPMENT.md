# Development environment

Development and firmware compilation run entirely in Docker. The host needs
only Git and Docker; Python, ESPHome, PlatformIO and compiler toolchains are not
installed on macOS.

The environment uses ESPHome's `YEAR.MONTH` image tag. The default is
`2026.6`, which follows compatible patch releases within that release line.

## First start

```sh
./scripts/dev build
./scripts/dev version
```

The first build downloads the official ESPHome image. PlatformIO toolchains,
generated firmware and ESPHome build caches are stored in named Docker volumes,
not in the repository or in host toolchain directories.

## Validate and compile

```sh
./scripts/dev config examples/minimal.yaml
./scripts/dev compile examples/minimal.yaml
```

Check the repository naming and dependency rules without compiling:

```sh
./scripts/check-repository
```

To execute another ESPHome command:

```sh
./scripts/dev run --help
```

## Flash from macOS without a host toolchain

Docker Desktop cannot pass a macOS `/dev/cu.*` device directly into its Linux
VM. The `flash` command uses the existing macOS Python standard library only as
a byte bridge; `esptool` still runs inside Docker and nothing is installed.

Put the ESP32-S3 into download mode (`STR_IO0` held while pressing `RST`), then
flash a factory image located inside the repository:

```sh
./scripts/dev flash artifacts/firmware.factory.bin /dev/cu.usbmodem101
```

Press `RST` once after the verified write completes. Python 3 is required only
for this optional macOS USB bridge, not for validation or compilation.

For an interactive shell inside the container:

```sh
./scripts/dev shell
```

## Test another ESPHome release line

Override the version for one invocation. A separate image and separate cache
volumes are used automatically:

```sh
ESPHOME_VERSION=2026.3 ./scripts/dev compile examples/minimal.yaml
```

## Cache volumes

The default volumes are:

- `lilygo-t5-47-plus-platformio-2026.6`
- `lilygo-t5-47-plus-cache-2026.6`

They can be inspected or removed with normal Docker volume commands. Removing
them is optional and only forces ESPHome to download/rebuild its containerized
toolchain and cache again.

## Continuous integration

GitHub Actions runs the same Docker workflow for ESPHome 2026.3 and 2026.6. It
validates all test configurations, compiles full component coverage on both
release lines and compiles the deep-sleep path on the current release line.
