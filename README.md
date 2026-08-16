# @aic/schemas

**Single Source of Truth** for JSON Schema data contracts in the **Evidence-First AI 3PL Invoice Reconciliation Engine** (COMPFEST 18 AI Innovation Challenge — Smart Logistics).

---

## 📌 Purpose

This repository holds canonical, versioned JSON Schema specifications (Draft 2020-12) used across the multi-service architecture:
- **`ai-service` (Python):** Validates structured extractions and bounding-box evidence payloads before returning to backend.
- **`backend-api` (Go):** Ingestion validation, deterministic pricing calculations, entity resolution, and reconciliation state.
- **`frontend` (TypeScript / Next.js):** Typed contracts for reviewer UI components and dispute package export.
- **`synthetic-data` (Python):** Ground truth specifications and synthetic transaction generators.

---

## 🗂️ Schema Inventory (`v0.1.0`)

| Schema File | Scope & Responsibility |
|---|---|
| [`canonical_schema.json`](v0.1.0/canonical_schema.json) | **Master `ShipmentEvent`** reconciling facts across Invoice, Surat Jalan, POD, Contract, and Pricing Engine. |
| [`invoice_schema.json`](v0.1.0/invoice_schema.json) | 3PL Invoice header, line items, rates, taxes, and bounding-box evidence. |
| [`pod_schema.json`](v0.1.0/pod_schema.json) | Proof of Delivery cargo status, receiver name, and signature / stamp presence detection. |
| [`surat_jalan_schema.json`](v0.1.0/surat_jalan_schema.json) | Dispatch order facts: actual scale weight, origin, destination, packages. |
| [`rate_agreement_schema.json`](v0.1.0/rate_agreement_schema.json) | Commercial rate cards compiled into machine-executable pricing rules. |
| [`ground_truth_schema.json`](v0.1.0/ground_truth_schema.json) | Benchmark ground truth transaction model for evaluation. |
| [`common/evidence.json`](v0.1.0/common/evidence.json) | Reusable bounding-box coordinate and confidence tracking model. |
| [`common/discrepancies.json`](v0.1.0/common/discrepancies.json) | Standardized taxonomy of discrepancy error codes and reconciliation statuses. |

---

## 🔄 Semantic Versioning

- Pinned version releases are stored under versioned directories (e.g., `v0.1.0/`).
- Root schema files (e.g., `canonical_schema.json`) reflect the latest stable baseline.
- All services pin their schema version via environment variable:
  ```env
  SCHEMA_VERSION=0.1.0
  ```

---

## 💻 Language Integration Guide

### 1. Python (`ai-service` & `synthetic-data`)
Generate Pydantic v2 models or validate dynamically:
```python
import json
from jsonschema import validate

# Load schema
with open("../schemas/v0.1.0/invoice_schema.json") as f:
    schema = json.load(f)

# Validate payload
validate(instance=extracted_invoice_payload, schema=schema)
```

### 2. Go (`backend-api`)
Validate JSON payloads using `gojsonschema`:
```go
import "github.com/xeipuuv/gojsonschema"

schemaLoader := gojsonschema.NewReferenceLoader("file://../schemas/v0.1.0/canonical_schema.json")
documentLoader := gojsonschema.NewGoLoader(shipmentEvent)

result, err := gojsonschema.Validate(schemaLoader, documentLoader)
if err != nil || !result.Valid() {
    // Handle validation errors
}
```

### 3. TypeScript (`frontend`)
Generate TypeScript interfaces using `json-schema-to-typescript`:
```bash
npx json-schema-to-typescript ../schemas/v0.1.0/canonical_schema.json > src/types/canonical.d.ts
```

---

## 🧪 Validating Schemas & Examples

Run the automated test validator:

```bash
python scripts/validate_schemas.py
```

Expected output:
```text
============================================================
 🔍 VALIDATING SCHEMAS & EXAMPLES (v0.1.0)
============================================================
✅ [JSON OK] v0.1.0/common/evidence.json
✅ [JSON OK] v0.1.0/common/discrepancies.json
✅ [JSON OK] v0.1.0/invoice_schema.json
✅ [JSON OK] v0.1.0/pod_schema.json
✅ [JSON OK] v0.1.0/surat_jalan_schema.json
✅ [JSON OK] v0.1.0/rate_agreement_schema.json
✅ [JSON OK] v0.1.0/canonical_schema.json
✅ [JSON OK] v0.1.0/ground_truth_schema.json

------------------------------------------------------------
 🧪 VALIDATING EXAMPLE PAYLOADS AGAINST SCHEMAS
------------------------------------------------------------
✅ [PASS] valid_invoice.json conforms to invoice_schema.json
✅ [PASS] valid_pod.json conforms to pod_schema.json
✅ [PASS] valid_surat_jalan.json conforms to surat_jalan_schema.json
✅ [PASS] valid_rate_agreement.json conforms to rate_agreement_schema.json
✅ [PASS] valid_canonical_event.json conforms to canonical_schema.json
✅ [PASS] valid_ground_truth.json conforms to ground_truth_schema.json

============================================================
 🎉 ALL SCHEMAS & EXAMPLES PASSED VALIDATION!
============================================================
```
