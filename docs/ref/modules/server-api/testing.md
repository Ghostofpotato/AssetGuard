# Testing

The Server API and Framework use `pytest` as the test runner. Tests are organized alongside each module.

---

## Test Locations

| Location | Scope |
|----------|-------|
| `framework/assetguard/tests/` | Interface layer unit tests |
| `framework/assetguard/core/tests/` | Core logic unit tests |
| `api/api/test/` | API layer unit tests |
| `api/api/controllers/test/` | Controller tests |
| `framework/assetguard/rbac/tests/` | RBAC unit tests |
| `framework/assetguard/core/indexer/tests/` | Indexer integration tests |

---

## Running Tests

```bash
export ASSETGUARD_REPO=<your_path>
PYTHONPATH=$ASSETGUARD_REPO/framework:$ASSETGUARD_REPO/api pytest framework --disable-warnings
```

### Running specific test modules

```bash
# Interface layer tests
PYTHONPATH=$ASSETGUARD_REPO/framework:$ASSETGUARD_REPO/api pytest framework/assetguard/tests/ --disable-warnings

# Core logic tests
PYTHONPATH=$ASSETGUARD_REPO/framework:$ASSETGUARD_REPO/api pytest framework/assetguard/core/tests/ --disable-warnings

# API layer tests
PYTHONPATH=$ASSETGUARD_REPO/framework:$ASSETGUARD_REPO/api pytest api/api/test/ --disable-warnings
```

---

## Configuration

The project uses `pytest.ini` files for test configuration. These are located at:
- `framework/pytest.ini`
- `api/api/pytest.ini`
