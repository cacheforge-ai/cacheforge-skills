# Changelog

## 0.1.0 (2026-02-15)

### Added
- Initial release
- **Plan analysis** (`plan` subcommand): runs `terraform plan -json`, parses streaming JSON output
- **Risk classification**: every resource change classified as 🟢 Safe, 🟡 Moderate, 🟠 Dangerous, or 🔴 Critical
- **Critical resource detection**: IAM roles/policies, security groups, KMS keys, databases (RDS, DynamoDB, Cloud SQL), S3 buckets, DNS records, WAF rules, CloudTrail
- **Dangerous resource detection**: EC2 instances, load balancers, ECS/EKS clusters, VPCs, subnets, NAT gateways, Lambda functions
- **Destroy/replace prominence**: destroyed resources shown in dedicated "💀 RESOURCES BEING DESTROYED" section
- **Drift detection**: identifies resources changed outside Terraform
- **Pre-apply checklist**: context-aware verification items based on plan contents
- **State inspection** (`state` subcommand): list and filter managed resources with category classification
- **Config validation** (`validate` subcommand): run `terraform validate -json` with structured output
- **OpenTofu support**: seamless `tofu` support via `TF_BINARY` env var with auto-detection
- **Dual output**: JSON to stdout (agent consumption) + Markdown to stderr (human-readable)
- **Timeout support**: configurable via `TF_PLAN_TIMEOUT` (default 600s), uses `timeout`/`gtimeout`
- **Safety**: strictly read-only, never runs `terraform apply`, never modifies state
- **Error handling**: clean JSON errors for missing tools, missing config, failed plans
- SKILL.md with comprehensive agent instructions including Terraform change type education
- SECURITY.md with threat model and abuse case mitigations
- TESTING.md with 12 test cases + security verification steps
