# Security model and responsible use

A PHIP registry entry is **a community metadata assertion**, not a certificate and not proof that software is safe.

- **Global collisions:** This repository only detects duplicates inside this registry. Other homebrew stores and official Sony title allocations may use the same IDs.
- **Publisher impersonation:** CI checks the PR author's GitHub login against `owner`, but does not cryptographically prove control of the linked source repository. Human reviewers must inspect this relationship, especially for organization-owned projects.
- **Malicious links/binaries:** Registration metadata is not a binary audit. Download clients must separately validate hashes, trusted origins, and package contents.
- **Compromised publishers:** A compromised GitHub account can make apparently legitimate updates; downstream consumers should pin reviewed revisions and enforce their own supply-chain trust decisions.
- **Installation safety:** Never overwrite unknown installed apps solely because the Title IDs match. Report conflicts and seek user consent before migration.
- **Claims/disputes:** File an identity-conflict issue with source links and evidence. Maintainers should investigate, not accept first-submitter priority as conclusive proof.
- **Data:** Only public project metadata should be submitted. Never include secrets, console keys, accounts, or private information.

Security issues affecting the registry tooling may be reported privately to the maintainer via GitHub's vulnerability reporting mechanism, if enabled; otherwise open an issue without publishing exploit secrets.
