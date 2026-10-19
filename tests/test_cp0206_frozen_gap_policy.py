import hashlib,json,unittest
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy.json"
R=ROOT/"evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy_SHA256.json"
EXPECTED="f8bdc5b034a65e6a9e906c3b80443e9cc149e3d922f6f6f763692cb38cfa8641"
KEYS=["1504713600000","1518062400000","1518076800000","1518091200000","1518105600000","1518120000000","1518134400000","1518148800000","1529985600000","1530000000000","1530676800000","1542168000000","1552363200000","1557892800000","1557907200000","1565841600000","1582113600000"]
class CP0206PolicyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.raw=P.read_bytes();cls.p=json.loads(cls.raw);cls.r=json.loads(R.read_text(encoding="utf-8"))
 def test_hash_receipt(self):
  d=hashlib.sha256(self.raw).hexdigest();self.assertEqual(d,EXPECTED);self.assertEqual(self.r["policy_sha256"],d);self.assertEqual(self.r["policy_bytes"],len(self.raw))
 def test_exact_17_keys_and_1_overlap_16_gap_only(self):
  rows=self.p["expected_missing_slots"];self.assertEqual([x["open_time_ms"] for x in rows],KEYS);self.assertEqual(len({x["open_time_ms"] for x in rows}),17);self.assertEqual(sum(x["classification"].startswith("EXISTING_ROW_CASE_OVERLAP") for x in rows),1);self.assertEqual(sum(x["classification"]=="GAP_WINDOW_ONLY" for x in rows),16)
 def test_4h_boundaries(self):
  for x in self.p["expected_missing_slots"]:
   a=datetime.fromisoformat(x["expected_open_time_utc"].replace("Z","+00:00"));b=datetime.fromisoformat(x["coverage_end_utc"].replace("Z","+00:00"));self.assertEqual((b-a).total_seconds(),14400);self.assertEqual(int(a.timestamp()*1000),int(x["open_time_ms"]))
 def test_no_g0_clearance_or_unsafe_authority(self):
  p=self.p;self.assertEqual(p["status"],"FROZEN_FOR_SENSITIVITY_ONLY_NOT_G0_CLEARANCE");self.assertEqual(p["scope"]["g0"],"BLOCKED_GLOBAL");self.assertEqual(p["scope"]["canonical_source"],"NONE");self.assertFalse(p["explicit_non_effects"]["candidate_build_authorized"]);self.assertFalse(p["explicit_non_effects"]["backtest_authorized"]);self.assertFalse(p["explicit_non_effects"]["quarantine_applied_to_candidate_builder"]);self.assertEqual(p["explicit_non_effects"]["live_signing_broadcast_orders"],"BLOCKED")
 def test_no_synthetic_candles_fills_or_duplicate_overlap(self):
  s=" ".join(self.p["policy_b"]["rules"]).lower();self.assertIn("do not synthesize missing candles",s);self.assertIn("do not create a duplicate row case",s);self.assertIn("do not invent an exit fill",s);self.assertIn("censored_gap_exposed",s)
 def test_warmup_and_independent_accounting_prerequisite(self):
  s=" ".join(self.p["policy_b"]["rules"]).lower();self.assertIn("each strategy's own warm-up",s);q=" ".join(self.p["independent_preconditions_before_any_sensitivity_runner"]).lower();self.assertIn("<= 1e-8 usdt",q);self.assertIn("non-tautological",q);self.assertIn("cp-0040",q)
 def test_frozen_source_hashes(self):
  f=self.p["frozen_inputs"];self.assertEqual(f["cp0040_rulebook_sha256"],"5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0");self.assertEqual(f["cp0200_recommendation_csv_sha256"],"e59c95764d4db76a8a707d07526d44b2b7e3487c534687584bd9936a5742b3bf");self.assertEqual(f["cp0201_crosswalk_csv_sha256"],"de8d829f405aa60f83e43744d4c281469fec6acb9bb99cfe6aa8823c8509be56");self.assertEqual(self.r["status"],self.p["status"])
if __name__=="__main__": unittest.main()
