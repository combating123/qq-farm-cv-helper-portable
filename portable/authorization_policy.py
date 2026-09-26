"""Source-owned entitlement validation used by release and runtime audits.

This module is intentionally read-only.  It validates an entitlement document
that was produced by the application's own authorization service or signer;
it does not create keys, rewrite license files, or modify a packaged binary.
The optional ``verifier`` callback keeps cryptographic verification outside the
small policy layer so the caller can use its existing Ed25519 implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional


Verifier = Callable[[Mapping[str, Any], Mapping[str, Any]], bool]


@dataclass(frozen=True)
class AuthorizationDecision:
    """Result of a read-only entitlement validation pass."""

    active: bool
    reason: str
    license_id: str = ""
    expires_at: Optional[int] = None
    features: frozenset[str] = frozenset()
    source_path: str = ""


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_present(mapping: Mapping[str, Any], names: Iterable[str]) -> Any:
    for name in names:
        if name in mapping and mapping[name] not in (None, ""):
            return mapping[name]
    return None


def _integer(value: Any) -> Optional[int]:
    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = int(float(str(value).strip()))
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if parsed > 0 else None


def _feature_names(claims: Mapping[str, Any]) -> frozenset[str]:
    raw = _first_present(claims, ("feature_flags", "features"))
    if not isinstance(raw, Mapping):
        return frozenset()
    return frozenset(
        str(name).strip()
        for name, enabled in raw.items()
        if str(name).strip() and bool(enabled)
    )


def _device_matches(expected: Any, supplied: Any) -> bool:
    if expected in (None, "") or supplied in (None, ""):
        return True
    expected_text = str(expected).strip().lower()
    supplied_text = str(supplied).strip().lower()
    if expected_text == supplied_text:
        return True
    return expected_text == hashlib.sha256(
        supplied_text.encode("utf-8")
    ).hexdigest()


def _inactive(
    reason: str,
    *,
    claims: Mapping[str, Any] | None = None,
    source_path: str = "",
) -> AuthorizationDecision:
    claims = claims or {}
    return AuthorizationDecision(
        active=False,
        reason=reason,
        license_id=str(claims.get("license_id", "") or ""),
        expires_at=_integer(
            _first_present(
                claims,
                (
                    "exp",
                    "expires_at_unix",
                    "expires_at",
                    "expire_at",
                    "card_expire_at",
                ),
            )
        ),
        features=_feature_names(claims),
        source_path=source_path,
    )


def validate_entitlement_document(
    document: Mapping[str, Any],
    *,
    product_id: str,
    now: int,
    verifier: Verifier | None = None,
    require_signature: bool = False,
    device_id: str | None = None,
    source_path: str = "",
) -> AuthorizationDecision:
    """Validate a source-owned entitlement document without changing it.

    The document may contain claims under ``claims`` or expose them at the
    top level.  A product identifier and a future expiry are mandatory.  When
    ``require_signature`` is enabled, a signature and a caller-supplied
    verifier are mandatory as well.
    """

    if not isinstance(document, Mapping):
        return _inactive("malformed-document", source_path=source_path)

    nested = document.get("claims")
    claims = _as_mapping(nested) if nested is not None else document
    if not claims:
        return _inactive("malformed-document", source_path=source_path)

    expected_product = str(product_id or "").strip()
    actual_product = str(
        _first_present(claims, ("product_id", "app_id", "product")) or ""
    ).strip()
    if not expected_product or not actual_product:
        return _inactive("product-missing", claims=claims, source_path=source_path)
    if actual_product != expected_product:
        return _inactive("product-mismatch", claims=claims, source_path=source_path)

    status = str(_first_present(claims, ("status", "state")) or "active").lower()
    if status not in {"active", "valid", "enabled"}:
        return _inactive("inactive-status", claims=claims, source_path=source_path)
    for flag_name in ("active", "valid"):
        if flag_name in claims and claims[flag_name] is False:
            return _inactive("inactive-flag", claims=claims, source_path=source_path)

    expires_at = _integer(
        _first_present(
            claims,
            ("exp", "expires_at_unix", "expires_at", "expire_at", "card_expire_at"),
        )
    )
    if expires_at is None:
        return _inactive("expiry-missing", claims=claims, source_path=source_path)
    if int(now) >= expires_at:
        return _inactive("expired", claims=claims, source_path=source_path)

    signature = _first_present(document, ("signature", "sig", "license_signature"))
    if require_signature and signature in (None, ""):
        return _inactive("signature-missing", claims=claims, source_path=source_path)
    if signature not in (None, ""):
        if verifier is None:
            if require_signature:
                return _inactive("verifier-missing", claims=claims, source_path=source_path)
        else:
            try:
                if not bool(verifier(document, claims)):
                    return _inactive("signature-invalid", claims=claims, source_path=source_path)
            except Exception:
                return _inactive("signature-error", claims=claims, source_path=source_path)

    expected_device = _first_present(claims, ("device_hash", "bound_hash"))
    if device_id not in (None, "") and not _device_matches(expected_device, device_id):
        return _inactive("device-mismatch", claims=claims, source_path=source_path)

    return AuthorizationDecision(
        active=True,
        reason="active",
        license_id=str(claims.get("license_id", "") or ""),
        expires_at=expires_at,
        features=_feature_names(claims),
        source_path=source_path,
    )


def read_entitlement_file(
    path: str | Path,
    *,
    product_id: str,
    now: int,
    verifier: Verifier | None = None,
    require_signature: bool = False,
    device_id: str | None = None,
) -> AuthorizationDecision:
    """Read and validate one entitlement file without writing to it."""

    source_path = str(path)
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _inactive("file-not-found", source_path=source_path)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _inactive("file-unreadable", source_path=source_path)
    return validate_entitlement_document(
        payload,
        product_id=product_id,
        now=now,
        verifier=verifier,
        require_signature=require_signature,
        device_id=device_id,
        source_path=source_path,
    )


def audit_entitlement_paths(
    paths: Iterable[str | Path],
    *,
    product_id: str,
    now: int,
    verifier: Verifier | None = None,
    require_signature: bool = False,
    device_id: str | None = None,
) -> AuthorizationDecision:
    """Return the first active result, otherwise the last observed reason."""

    last = _inactive("no-candidates")
    for path in paths:
        decision = read_entitlement_file(
            path,
            product_id=product_id,
            now=now,
            verifier=verifier,
            require_signature=require_signature,
            device_id=device_id,
        )
        if decision.active:
            return decision
        last = decision
    return last
