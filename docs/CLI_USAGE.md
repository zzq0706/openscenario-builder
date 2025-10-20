# OpenSCENARIO Validator CLI Usage Guide

The `openscenario-validate` command-line tool provides a simple way to validate OpenSCENARIO files against the schema. It's designed for both manual use and integration into CI/CD pipelines.

## Installation

After installing the `openscenario-builder` package:

```bash
pip install openscenario-builder
```

The `openscenario-validate` command will be available in your PATH.

## Basic Usage

### Validate a Single File

```bash
openscenario-validate scenario.xosc
```

### Validate Multiple Files

```bash
openscenario-validate scenario1.xosc scenario2.xosc scenario3.xosc
```

### Validate All Files in a Directory

```bash
openscenario-validate scenarios/
```

This will recursively find all `.xosc` files in the directory.

### Validate with Wildcards

```bash
# Validate all .xosc files in current directory
openscenario-validate *.xosc

# Validate all .xosc files recursively
openscenario-validate "**/*.xosc"

# Validate files matching a pattern
openscenario-validate "tests/test_*.xosc"
```

**Note:** On Windows PowerShell, quote the wildcard patterns to prevent shell expansion.

## Command-Line Options

### `--schema` / `-s`
Specify a custom schema file (default: auto-detected)

```bash
openscenario-validate --schema custom_schema.xsd scenario.xosc
```

### `--verbose` / `-v`
Show detailed validation errors

```bash
openscenario-validate --verbose scenario.xosc
```

Example output:
```
✗ INVALID: scenario.xosc
  1. Element 'Action': Missing required child element 'PrivateAction'
  2. Element 'Maneuver': Attribute 'name' is required
```

### `--quiet` / `-q`
Minimal output (only summary)

```bash
openscenario-validate --quiet scenarios/
```

Example output:
```
3/5 valid
```

### `--fail-fast`
Stop validation on the first error

```bash
openscenario-validate --fail-fast scenarios/
```

Useful for quickly identifying the first problematic file in a large batch.

### `--version`
Display version information

```bash
openscenario-validate --version
```

## Exit Codes

The validator returns specific exit codes for different scenarios:

- **0**: All files are valid
- **1**: One or more files are invalid or validation failed
- **2**: Command-line arguments error (e.g., file not found, invalid options)

This makes it easy to use in CI/CD pipelines and scripts.

## CI/CD Integration

### GitHub Actions

```yaml
name: Validate OpenSCENARIO Files

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install validator
      run: pip install openscenario-builder
    
    - name: Validate scenarios
      run: openscenario-validate --verbose scenarios/
```

### GitLab CI

```yaml
validate_scenarios:
  stage: test
  image: python:3.9
  
  before_script:
    - pip install openscenario-builder
  
  script:
    - openscenario-validate --verbose scenarios/
  
  only:
    - merge_requests
    - main
```

### Azure Pipelines

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'
  
- script: |
    pip install openscenario-builder
  displayName: 'Install validator'

- script: |
    openscenario-validate --verbose scenarios/
  displayName: 'Validate OpenSCENARIO files'
```

### Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Validate Scenarios') {
            steps {
                sh '''
                    pip install openscenario-builder
                    openscenario-validate --verbose scenarios/
                '''
            }
        }
    }
}
```

### CircleCI

```yaml
version: 2.1

jobs:
  validate:
    docker:
      - image: python:3.9
    
    steps:
      - checkout
      
      - run:
          name: Install validator
          command: pip install openscenario-builder
      
      - run:
          name: Validate scenarios
          command: openscenario-validate --verbose scenarios/

workflows:
  version: 2
  build:
    jobs:
      - validate
```

## Advanced Usage Examples

### Pre-commit Hook

Create a `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-openscenario
        name: Validate OpenSCENARIO files
        entry: openscenario-validate
        language: system
        files: \.xosc$
        pass_filenames: true
```

### Shell Script for Batch Validation

```bash
#!/bin/bash
# validate_all.sh

echo "Validating OpenSCENARIO files..."

if openscenario-validate --verbose scenarios/; then
    echo "✓ All scenarios are valid!"
    exit 0
else
    echo "✗ Validation failed!"
    exit 1
fi
```

### PowerShell Script (Windows)

```powershell
# validate_all.ps1

Write-Host "Validating OpenSCENARIO files..." -ForegroundColor Cyan

$result = & openscenario-validate --verbose scenarios/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All scenarios are valid!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ Validation failed!" -ForegroundColor Red
    exit 1
}
```

### Make Target

Add to your `Makefile`:

```makefile
.PHONY: validate-scenarios
validate-scenarios:
	@echo "Validating OpenSCENARIO files..."
	@openscenario-validate --verbose scenarios/

.PHONY: validate-scenarios-quiet
validate-scenarios-quiet:
	@openscenario-validate --quiet scenarios/
```

Usage:
```bash
make validate-scenarios
```

## Troubleshooting

### Schema Not Found

If the validator cannot find the default schema:

```bash
openscenario-validate --schema /path/to/OpenSCENARIO_v1_3.xsd scenario.xosc
```

### No Files Found

When using wildcards, ensure they're properly quoted:

```bash
# Good
openscenario-validate "scenarios/**/*.xosc"

# May not work as expected
openscenario-validate scenarios/**/*.xosc
```

### Verbose Output for Debugging

Use `--verbose` to see detailed error messages:

```bash
openscenario-validate --verbose scenario.xosc
```

### Checking Specific Files in CI

To validate only changed files in a CI pipeline:

```bash
# GitHub Actions
git diff --name-only origin/main... | grep '\.xosc$' | xargs openscenario-validate --verbose

# Generic
git diff --diff-filter=ACMR --name-only HEAD~1 | grep '\.xosc$' | xargs -r openscenario-validate --verbose
```

## Output Examples

### Valid File

```
Validating 1 file(s) against schema...

======================================================================
VALIDATION RESULTS
======================================================================

✓ VALID: scenario.xosc

======================================================================
SUMMARY: 1/1 files valid, 0 invalid
======================================================================
```

### Invalid File (Normal Mode)

```
Validating 1 file(s) against schema...

======================================================================
VALIDATION RESULTS
======================================================================

✗ INVALID: scenario.xosc
  3 error(s) found (use --verbose for details)

======================================================================
SUMMARY: 0/1 files valid, 1 invalid
======================================================================
```

### Invalid File (Verbose Mode)

```
Validating 1 file(s) against schema...

======================================================================
VALIDATION RESULTS
======================================================================

✗ INVALID: scenario.xosc
  1. Element 'Init': Missing required child element 'Actions'
  2. Element 'Maneuver': Attribute 'name' is required but not present
  3. Element 'Story': Must contain at least 1 'Act' element

======================================================================
SUMMARY: 0/1 files valid, 1 invalid
======================================================================
```

### Quiet Mode

```
3/5 valid
```

## Best Practices

1. **Use in CI/CD**: Integrate validation into your continuous integration pipeline to catch errors early.

2. **Verbose in CI**: Use `--verbose` in CI environments to get detailed error messages in logs.

3. **Fail Fast for Development**: Use `--fail-fast` during development to quickly identify the first error.

4. **Quiet for Scripts**: Use `--quiet` when calling from scripts that parse the output.

5. **Custom Schemas**: If you have custom schema extensions, use `--schema` to specify your schema.

6. **Validate on Commit**: Use pre-commit hooks to validate files before they're committed.

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/your-org/openscenario-builder/issues
- Documentation: https://openscenario-builder.readthedocs.io/
