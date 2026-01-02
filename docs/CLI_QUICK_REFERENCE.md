# OpenSCENARIO Validator - Quick Reference

The `openscenario-validate` command-line tool provides a simple way to validate OpenSCENARIO files against the schema. It's designed for both manual use and integration into CI/CD pipelines.

## Installation

See [README.md](../README.md) for complete documentation.

## Basic Commands

```bash
# Single file
openscenario-validate scenario.xosc

# Multiple files
openscenario-validate file1.xosc file2.xosc file3.xosc

# All files in directory (recursive)
openscenario-validate scenarios/

# With wildcards
openscenario-validate "tests/**/*.xosc"
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--schema` | `-s` | Custom schema file |
| `--verbose` | `-v` | Show detailed errors |
| `--quiet` | `-q` | Minimal output |
| `--fail-fast` | | Stop on first error |
| `--help` | `-h` | Show help |
| `--version` | | Show version |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All files valid ✓ |
| `1` | Invalid files or error ✗ |
| `2` | Command-line error |

## CI/CD Examples

### GitHub Actions
```yaml
- name: Validate scenarios
  run: openscenario-validate --verbose scenarios/
```

### GitLab CI
```yaml
validate:
  script:
    - openscenario-validate --verbose scenarios/
```

### Jenkins
```groovy
sh 'openscenario-validate --verbose scenarios/'
```

## Common Use Cases

```bash
# Development: Quick check
openscenario-validate scenario.xosc

# CI/CD: Detailed output
openscenario-validate --verbose scenarios/

# Pre-commit: Fast fail
openscenario-validate --fail-fast *.xosc

# Script: Parse output
openscenario-validate --quiet scenarios/
```
