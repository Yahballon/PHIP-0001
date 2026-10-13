# Contributing to PHIP-0001

PHIP-0001 is an open community draft. Technical objections and alternative models are welcome. All contributions should be written in English.

## Register an application

1. Read [PHIP-0001](docs/PHIP-0001.md) and browse the [current registry](REGISTRY.md).
2. Check for an existing allocation in [the PS5 Homebrew Catalog](https://github.com/blackbearreloaded/ps5-homebrew-catalog/tree/main/apps), as well as any other relevant community store.
3. Fork this repository. **Do not copy** the sample's `PPSA12345` or boilerplate `PPSA99999`.
4. Create `registry/PPSAxxxxx.json` using [the sample](examples/registration.example.json). Your `owner` must match your GitHub account and the account in your `source_repo` URL.
5. Run the checks:

   ```bash
   python tools/validate_registry.py
   python -m unittest discover -s tests -v
   python tools/build_index.py
   ```

6. Include the generated `index/registry.json`, `index/stats.json`, and `REGISTRY.md` in your PR.
7. Open a PR from the same account that owns your app. Include evidence that you control your GitHub source repository and links to any external registrations of your title.
8. A maintainer checks claims, reviews collisions, and merges if appropriate. CI passing is **not** automatic acceptance.

For an organization account, the organization may have to submit using a dedicated maintainer account until governance supports delegated organization verification. Do not claim you own another developer's namespace.

## App updates

Use the same `title_id` and `app_id` across versions. PHIP-0001 does not require a new registration for each release; release versions belong in the application repository. You may update human-readable name, description, license or registration status through review.

## Transfers and disputes

To change project ownership, rename namespaces, retire IDs, or resolve disputed allocations, open an issue explaining the project history and ownership. Maintainers will review manually; these identity fields are intentionally immutable in ordinary PRs.

## Coding standards

- Python 3.10+, standard library only for registry maintenance tools.
- JSON: UTF-8, two-space indentation, clear field names.
- Generated indexes must be deterministic and committed with registration changes.
- CI on pull requests must not use privileged credentials or execute code from registered app repositories.
- No piracy, proprietary firmware, keys or credentials.
