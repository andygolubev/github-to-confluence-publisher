# Validation, TLS, and failure modes

The publisher tries to fail early on configuration mistakes and malformed API responses so a bad run is obvious before content drift becomes hard to trace.

![Validation checks, TLS handling, and response guards](/data_images/validation-guardrails.svg)

## Guardrails in the current code

| Check | Where it happens | What it prevents |
|---|---|---|
| Credential presence | `main.py` | Empty login or token runs |
| URL normalization | `config/confluence_url.py` | Using the wiki home URL instead of the REST API base |
| Space key and parent id validation | `config/get_config.py` | Invalid CQL inputs and non-numeric page ids |
| Parent page verification | `ConfluenceClient.verify_parent_page_exists()` | Publishing beneath a missing or misconfigured ancestor |
| HTML-vs-JSON detection | `_confluence_request_error_message()` | Misleading API failures when the URL points at an HTML page |
| Pydantic response validation | `confluence_api_models.py` | Silent schema drift in Confluence responses |
| TLS verification | `requests` defaults and the container CA store | Insecure `verify=False` behavior |

## TLS details

The code never disables certificate verification. Requests use the system trust store, and the container entrypoint refreshes that store so mounted custom CAs become active before any Confluence call.

## Failure shapes you should expect

- Wrong parent id: hard failure before any create or delete calls.
- Wrong Confluence URL: runtime error that explains HTML was returned instead of JSON.
- Bad response payload: `ConfluenceApiValidationError` with the expected schema context.
- Missing attachment file: logged error, page publish continues.
- Space mismatch between config and parent page: warning only, because Confluence may still accept the page create depending on the target.
