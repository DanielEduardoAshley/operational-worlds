# Operational Worlds Design Engine

Current target:

```text
0.2.0-alpha.1
```

## Development

Install test dependencies:

```sh
python3 -m pip install -r requirements-dev.txt
```

Run tests:

```sh
python3 -m pytest
```

Build the Blender add-on zip:

```sh
python3 scripts/build_addon.py
```

The build artifact will be written to:

```text
dist/owde-0.2.0-alpha.1.zip
```
