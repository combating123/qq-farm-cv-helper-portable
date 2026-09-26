import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "portable" / "authorization_policy.py"
VERIFY_PATH = ROOT / "scripts" / "verify_authorization_delivery.py"


def load_policy_module():
    if not MODULE_PATH.is_file():
        raise AssertionError(
            "authorization policy module is not part of the delivery"
        )
    spec = importlib.util.spec_from_file_location(
        "qqfarm_authorization_policy", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_verifier_module():
    if not VERIFY_PATH.is_file():
        raise AssertionError("authorization delivery verifier is missing")
    spec = importlib.util.spec_from_file_location(
        "qqfarm_authorization_delivery_verifier", VERIFY_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AuthorizationDeliveryTests(unittest.TestCase):
    PRODUCT = "qq-farm-cv-helper"

    def test_active_document_requires_product_and_reports_features(self):
        policy = load_policy_module()
        decision = policy.validate_entitlement_document(
            {
                "claims": {
                    "product_id": self.PRODUCT,
                    "license_id": "DEV-001",
                    "status": "active",
                    "active": True,
                    "valid": True,
                    "exp": 2_000_000_000,
                    "feature_flags": {
                        "friend_patrol": True,
                        "quad_act_seeds": False,
                    },
                }
            },
            product_id=self.PRODUCT,
            now=1_900_000_000,
        )
        self.assertTrue(decision.active)
        self.assertEqual("active", decision.reason)
        self.assertEqual("DEV-001", decision.license_id)
        self.assertIn("friend_patrol", decision.features)
        self.assertNotIn("quad_act_seeds", decision.features)

    def test_expired_or_wrong_product_document_is_inactive(self):
        policy = load_policy_module()
        expired = policy.validate_entitlement_document(
            {"claims": {"product_id": self.PRODUCT, "exp": 100}},
            product_id=self.PRODUCT,
            now=101,
        )
        wrong_product = policy.validate_entitlement_document(
            {"claims": {"product_id": "other-product", "exp": 2_000}},
            product_id=self.PRODUCT,
            now=101,
        )
        self.assertFalse(expired.active)
        self.assertEqual("expired", expired.reason)
        self.assertFalse(wrong_product.active)
        self.assertEqual("product-mismatch", wrong_product.reason)

    def test_required_signature_is_checked_without_generating_or_mutating_keys(self):
        policy = load_policy_module()
        document = {
            "claims": {
                "product_id": self.PRODUCT,
                "status": "active",
                "active": True,
                "valid": True,
                "exp": 2_000,
            }
        }
        missing = policy.validate_entitlement_document(
            document,
            product_id=self.PRODUCT,
            now=100,
            require_signature=True,
            verifier=lambda _doc, _claims: True,
        )
        rejected = policy.validate_entitlement_document(
            dict(document, signature="fixture-signature"),
            product_id=self.PRODUCT,
            now=100,
            require_signature=True,
            verifier=lambda _doc, _claims: False,
        )
        accepted = policy.validate_entitlement_document(
            dict(document, signature="fixture-signature"),
            product_id=self.PRODUCT,
            now=100,
            require_signature=True,
            verifier=lambda _doc, _claims: True,
        )
        self.assertFalse(missing.active)
        self.assertEqual("signature-missing", missing.reason)
        self.assertFalse(rejected.active)
        self.assertEqual("signature-invalid", rejected.reason)
        self.assertTrue(accepted.active)

    def test_file_audit_is_read_only_and_skips_invalid_candidates(self):
        policy = load_policy_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid = root / "invalid.json"
            valid = root / "valid.json"
            invalid.write_text("{}", encoding="utf-8")
            valid.write_text(
                json.dumps(
                    {
                        "claims": {
                            "product_id": self.PRODUCT,
                            "status": "active",
                            "active": True,
                            "valid": True,
                            "exp": 2_000,
                        }
                    }
                ),
                encoding="utf-8",
            )
            before = valid.read_bytes()
            decision = policy.audit_entitlement_paths(
                [invalid, valid],
                product_id=self.PRODUCT,
                now=100,
            )
            self.assertTrue(decision.active)
            self.assertEqual("active", decision.reason)
            self.assertEqual(before, valid.read_bytes())

    def test_release_gate_requires_policy_and_document_but_rejects_v237_sample(self):
        verifier = load_verifier_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "portable").mkdir()
            (root / "docs").mkdir()
            (root / "portable" / "authorization_policy.py").write_text(
                "# fixture\n", encoding="utf-8"
            )
            (root / "docs" / "AUTHORIZATION_DELIVERY.md").write_text(
                "source-owned validation; offline comparison only\n",
                encoding="utf-8",
            )
            self.assertEqual([], verifier.check_delivery_tree(root))
            (root / "QQFarmCVHelper_v2.3.7_x64_setup.exe").write_bytes(b"fixture")
            issues = verifier.check_delivery_tree(root)
            self.assertTrue(any("v2.3.7" in issue for issue in issues))

            standalone = root / "v2.3.7-standalone"
            standalone.mkdir()
            (standalone / "QQFarmCVHelper.exe").write_bytes(b"fixture")
            issues = verifier.check_delivery_tree(root)
            self.assertTrue(any("standalone" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
