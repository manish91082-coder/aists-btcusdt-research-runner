# CP-0257: 11 aggregation blockers, exact-source and candidate-dependency crosswalk (Hindi)

**Status:** TRACEABILITY CROSSWALK COMPLETE; SOURCE ADJUDICATION NOT COMPLETE; G0 `BLOCKED_GLOBAL`.  
**Branch at start:** `cp-0165-4h-archive-audit`  
**Parent HEAD at start:** `3d21c951130a258207f94d61007f6c8f6bc87f1c`  
**Frozen CP-0040 rulebook blob:** `f0d0e81ea6708a0abeb34676f3ff12859080a3c7`; package-member SHA-256 `5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0`.  
**No source data downloaded or modified in this checkpoint. No backtest run.**

## 1. Purpose and evidence sources

This bounded checkpoint links all 11 frozen aggregation case IDs to the already-committed CP-0107 78-row raw source evidence, CP-0107 per-bucket roll-up comparison, and CP-0040 candidate-input relevance matrix. It is evidence traceability only. It does not select a canonical source, adjudicate historical version authority, apply Policy B, close a source case, or override a frozen gate.

- CP-0107 row evidence: `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_RowEvidence.csv`; Git blob `5ccb7fc91b829b4599de73f3b63683fbf1d5ebb9`; 78 rows.
- CP-0107 bucket comparison: `evidence/source_adjudication/CP0107_Run_38776970911/CP0107_CP0041_AggregationBucket_Comparison.csv`; Git blob `5dae35e8d420b3997be90cabc263825e98b8b918`; 11 cases.
- CP-0040 candidate-input matrix: `evidence/source_adjudication/CP0040_Candidate_Input_Relevance_Run_38901790221/CP0040_Candidate_Input_Relevance_Matrix.csv`; Git blob `2ae5c36aa1f370cb143f8a30d5a61f41be0d60eb`; 11 cases.
- Frozen blocker ledger: `evidence/source_adjudication/CP0040_Run_38883792900/CP0040_NonRow_Blockers.csv`; Git blob `d3fca23bac424fa8c8b187434e8c63e8d188a0e1`.
- CP-0107 aggregation source snapshot: `evidence/source_adjudication/CP0107_CP0041_Residual_Aggregation_Bucket_SourceSnapshot.csv`; Git blob `6e32188472ab45b43e1b90fe138399818c937277`.

## 2. Verified aggregate findings

- Case count: **11**; linked raw source-row records: **78**.
- Daily child roll-up matches daily parent: **11/11**.
- Frozen monthly mismatch signature reproduced: **11/11**.
- Monthly child-volume sum equals the frozen aggregate numeric text: **10/11**. `AGG-10` remains a reported non-exact numeric match (`279.26867100000004` vs `279.26867100`); this record does not normalize or dismiss it.
- Monthly child trade-count sums match frozen counts: **11/11**.
- Candidate matrix reports direct interval overlap with the `MTF_BREAKOUT_4H_D1` comparator as `False` for **11/11**. This is a narrow dependency observation, not source authority and not global clearance.

## 3. Per-case roll-up and dependency matrix

| Case | UTC bucket | Frozen monthly mismatch fields | Frozen → recomputed monthly child volume (exact-match flag) | Frozen → recomputed trade count (match flag) | Daily roll-up | Direct 4h/D1 overlap |
|---|---|---|---|---|---|---|
| AGG-01-5m-15m-2017-12-04T09:00:00Z | 2017-12-04T09:00:00Z | low;close;volume | 5.555226 → 5.55522600 (True) | 46 → 46 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-02-5m-15m-2017-12-04T09:15:00Z | 2017-12-04T09:15:00Z | open;high;volume | 9.125577 → 9.12557700 (True) | 101 → 101 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-03-5m-15m-2018-02-05T10:00:00Z | 2018-02-05T10:00:00Z | volume | 242.196971 → 242.19697100 (True) | 2859 → 2859 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-04-5m-15m-2018-03-04T14:30:00Z | 2018-03-04T14:30:00Z | high;low;volume | 21.246966 → 21.24696600 (True) | 411 → 411 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-05-5m-15m-2018-03-04T14:45:00Z | 2018-03-04T14:45:00Z | open;high;low;volume | 40.858444 → 40.85844400 (True) | 423 → 423 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-06-5m-15m-2018-09-05T09:45:00Z | 2018-09-05T09:45:00Z | volume | 3381.687979 → 3381.68797900 (True) | 15486 → 15486 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-07-15m-30m-2017-12-04T09:00:00Z | 2017-12-04T09:00:00Z | volume | 27.266735 → 27.26673500 (True) | 343 → 343 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-08-15m-30m-2018-02-07T06:30:00Z | 2018-02-07T06:30:00Z | volume | 679.189685 → 679.18968500 (True) | 6481 → 6481 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-09-15m-30m-2018-03-04T14:30:00Z | 2018-03-04T14:30:00Z | volume | 183.64649 → 183.64649000 (True) | 2171 → 2171 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-10-15m-30m-2018-06-20T03:30:00Z | 2018-06-20T03:30:00Z | volume | 279.26867100000004 → 279.26867100 (False) | 2277 → 2277 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |
| AGG-11-30m-1h-2018-03-20T03:00:00Z | 2018-03-20T03:00:00Z | volume | 1916.022665 → 1916.02266500 (True) | 11745 → 11745 (True) | DAILY_CHILD_ROLLUP_MATCHES_DAILY_PARENT | False |

## 4. Exact archive identity and sidecar lineage

The following are the exact source archive SHA-256 values recorded in the linked 78-row evidence. Daily sidecar hashes are recorded separately. These establish identity/integrity links for the observed files, not which version was historically authoritative at the time of publication.

### AGG-01-5m-15m-2017-12-04T09:00:00Z
- Bucket: `2017-12-04T09:00:00Z`; relationship: `5m → 15m`; row evidence records: 8.
- Monthly child: `BTCUSDT-5m-2017-12.zip SHA256=fab87582c0bfd79f200dfbbeebbce39fabf7c137c768daa867d9d688f64c6b19`.
- Monthly parent: `BTCUSDT-15m-2017-12.zip SHA256=a737d013096403196346f6297fe21fce7e3e8f7b6366e517535d9835eeb2fdf4`.
- Daily child: `BTCUSDT-5m-2017-12-04.zip SHA256=2d58f4ef76ecffe0764546bb13c6e304a862ec038d2f367a8f306d4badc7693e; sidecar SHA256=e43f46de3ec5185336e71a4cbfdfbfefb0041b75bc47be14991b0546afba64dd`.
- Daily parent: `BTCUSDT-15m-2017-12-04.zip SHA256=909b18ee1bb2e2269a2a763ae1c76ebe3b01db433c9e7055ddd95e7b9839940f; sidecar SHA256=cb88e27b62c3137838bdfd0aa44f5890fbda9865fd320adcb8fe0451d111bf1c`.
- Frozen monthly mismatch fields: `low;close;volume`; primary fields: `close;low;volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-02-5m-15m-2017-12-04T09:15:00Z
- Bucket: `2017-12-04T09:15:00Z`; relationship: `5m → 15m`; row evidence records: 8.
- Monthly child: `BTCUSDT-5m-2017-12.zip SHA256=fab87582c0bfd79f200dfbbeebbce39fabf7c137c768daa867d9d688f64c6b19`.
- Monthly parent: `BTCUSDT-15m-2017-12.zip SHA256=a737d013096403196346f6297fe21fce7e3e8f7b6366e517535d9835eeb2fdf4`.
- Daily child: `BTCUSDT-5m-2017-12-04.zip SHA256=2d58f4ef76ecffe0764546bb13c6e304a862ec038d2f367a8f306d4badc7693e; sidecar SHA256=e43f46de3ec5185336e71a4cbfdfbfefb0041b75bc47be14991b0546afba64dd`.
- Daily parent: `BTCUSDT-15m-2017-12-04.zip SHA256=909b18ee1bb2e2269a2a763ae1c76ebe3b01db433c9e7055ddd95e7b9839940f; sidecar SHA256=cb88e27b62c3137838bdfd0aa44f5890fbda9865fd320adcb8fe0451d111bf1c`.
- Frozen monthly mismatch fields: `open;high;volume`; primary fields: `high;open;volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-03-5m-15m-2018-02-05T10:00:00Z
- Bucket: `2018-02-05T10:00:00Z`; relationship: `5m → 15m`; row evidence records: 8.
- Monthly child: `BTCUSDT-5m-2018-02.zip SHA256=44bc33f321fbc4a4dd5c99bec7bbb4ca86e5cc33ddc6459610a18db7ae872c0b`.
- Monthly parent: `BTCUSDT-15m-2018-02.zip SHA256=9b7f75cef2aefea621bfedb0f136f15fc60aed5e6f4da1c521765a4c267123e0`.
- Daily child: `BTCUSDT-5m-2018-02-05.zip SHA256=a8832f5595a15373e9354685f2179c737b46127a8e88484498679e4b83cd65a4; sidecar SHA256=57782cf82de2e1f02b3d47732b028b951a797a7561217d88942d746895ca1550`.
- Daily parent: `BTCUSDT-15m-2018-02-05.zip SHA256=0f69d7e0e88a81fffeb4e8cb299bcf80fdd49da7dd99869f5b3e2561af6d51fc; sidecar SHA256=8d77de7ab7029c00d26b06a87ceb1d308ce909c1fb665b2764db515c35f020e3`.
- Frozen monthly mismatch fields: `volume`; primary fields: `volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-04-5m-15m-2018-03-04T14:30:00Z
- Bucket: `2018-03-04T14:30:00Z`; relationship: `5m → 15m`; row evidence records: 8.
- Monthly child: `BTCUSDT-5m-2018-03.zip SHA256=9f79a89dad86fbce45f7be8f0487e115a4e8d609b4c415b5a32781e823df0cd4`.
- Monthly parent: `BTCUSDT-15m-2018-03.zip SHA256=52982e2c0ceb520365cf320c631fd0603aff6d0b0b0a81d06e2c23f5a81e8be2`.
- Daily child: `BTCUSDT-5m-2018-03-04.zip SHA256=56e67ffe2108239a15a6955bcd0b1324337ba8eb3ed2d7b8434e1367b45b83fc; sidecar SHA256=06241af728c9b0d2cecd6378e32df0c711c8b2b13aca6e5237680c518d224034`.
- Daily parent: `BTCUSDT-15m-2018-03-04.zip SHA256=e466638b5103fd169f4976807db249215d120326172c0567e56280d16756408f; sidecar SHA256=a0243bd96bd70810e1e78b8b3190ce0b2806e62f30a3e97af6456be3f2cc93f7`.
- Frozen monthly mismatch fields: `high;low;volume`; primary fields: `high;low;volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-05-5m-15m-2018-03-04T14:45:00Z
- Bucket: `2018-03-04T14:45:00Z`; relationship: `5m → 15m`; row evidence records: 8.
- Monthly child: `BTCUSDT-5m-2018-03.zip SHA256=9f79a89dad86fbce45f7be8f0487e115a4e8d609b4c415b5a32781e823df0cd4`.
- Monthly parent: `BTCUSDT-15m-2018-03.zip SHA256=52982e2c0ceb520365cf320c631fd0603aff6d0b0b0a81d06e2c23f5a81e8be2`.
- Daily child: `BTCUSDT-5m-2018-03-04.zip SHA256=56e67ffe2108239a15a6955bcd0b1324337ba8eb3ed2d7b8434e1367b45b83fc; sidecar SHA256=06241af728c9b0d2cecd6378e32df0c711c8b2b13aca6e5237680c518d224034`.
- Daily parent: `BTCUSDT-15m-2018-03-04.zip SHA256=e466638b5103fd169f4976807db249215d120326172c0567e56280d16756408f; sidecar SHA256=a0243bd96bd70810e1e78b8b3190ce0b2806e62f30a3e97af6456be3f2cc93f7`.
- Frozen monthly mismatch fields: `open;high;low;volume`; primary fields: `high;low;open;volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-06-5m-15m-2018-09-05T09:45:00Z
- Bucket: `2018-09-05T09:45:00Z`; relationship: `5m → 15m`; row evidence records: 8.
- Monthly child: `BTCUSDT-5m-2018-09.zip SHA256=820d494c55b1b0149872f54af63d8245a98c48d83ede5f8b949ee49f42b52704`.
- Monthly parent: `BTCUSDT-15m-2018-09.zip SHA256=17c6956d455bcba50c83a17fb04f5c84feddfd3f217cbb117c3f6fe8fe366667`.
- Daily child: `BTCUSDT-5m-2018-09-05.zip SHA256=80396c452ecba3c2da0446755abe3cf945777a9cd5aa24017fcaec7d168073d2; sidecar SHA256=b08183196d4b5957af844b6ece8d0ed21211b26caa7b486aede9e88ec7b82796`.
- Daily parent: `BTCUSDT-15m-2018-09-05.zip SHA256=c8d66ceb83dbcca347b2d8329fbd7d0e3de8f69669caef672e21a0e322fa4d14; sidecar SHA256=a6aabd62a8c86e0106f695833176908e80c5f4360d676688f5b62b15cadd24b7`.
- Frozen monthly mismatch fields: `volume`; primary fields: `volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-07-15m-30m-2017-12-04T09:00:00Z
- Bucket: `2017-12-04T09:00:00Z`; relationship: `15m → 30m`; row evidence records: 6.
- Monthly child: `BTCUSDT-15m-2017-12.zip SHA256=a737d013096403196346f6297fe21fce7e3e8f7b6366e517535d9835eeb2fdf4`.
- Monthly parent: `BTCUSDT-30m-2017-12.zip SHA256=c64fcc280bc444ad7508982d526198373812e3ed44804969dc0d2b57da39517b`.
- Daily child: `BTCUSDT-15m-2017-12-04.zip SHA256=909b18ee1bb2e2269a2a763ae1c76ebe3b01db433c9e7055ddd95e7b9839940f; sidecar SHA256=cb88e27b62c3137838bdfd0aa44f5890fbda9865fd320adcb8fe0451d111bf1c`.
- Daily parent: `BTCUSDT-30m-2017-12-04.zip SHA256=64ff524726cd55639e9ed56fd59e276e6ffc6c496e19357713a8816d21e9767e; sidecar SHA256=7dc2a111681676b22e9cff9cf674740021e4704d74fac7e49f975d3ac7a9e8cc`.
- Frozen monthly mismatch fields: `volume`; primary fields: `volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-08-15m-30m-2018-02-07T06:30:00Z
- Bucket: `2018-02-07T06:30:00Z`; relationship: `15m → 30m`; row evidence records: 6.
- Monthly child: `BTCUSDT-15m-2018-02.zip SHA256=9b7f75cef2aefea621bfedb0f136f15fc60aed5e6f4da1c521765a4c267123e0`.
- Monthly parent: `BTCUSDT-30m-2018-02.zip SHA256=e14dc22f1ede6a9ae50130101de3fefb8ddf06220cb3e6afae9315b441e66681`.
- Daily child: `BTCUSDT-15m-2018-02-07.zip SHA256=0f1d760a85010d35d4d2b2cce8d2f4e20fba1ff54705f1162154545b69104e68; sidecar SHA256=e89fb1810b4b2255d0c1574f8eff835d74640a3bc9d4cb3932ef31e3315d9eee`.
- Daily parent: `BTCUSDT-30m-2018-02-07.zip SHA256=175826ce9dea0752730697568a2d702e48c684c71634076bd50fab3ab8ac6e28; sidecar SHA256=b614921b2c44a1f70407459b5d3178efedf0c69e63b10c82f205d9ea23ee950b`.
- Frozen monthly mismatch fields: `volume`; primary fields: `volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-09-15m-30m-2018-03-04T14:30:00Z
- Bucket: `2018-03-04T14:30:00Z`; relationship: `15m → 30m`; row evidence records: 6.
- Monthly child: `BTCUSDT-15m-2018-03.zip SHA256=52982e2c0ceb520365cf320c631fd0603aff6d0b0b0a81d06e2c23f5a81e8be2`.
- Monthly parent: `BTCUSDT-30m-2018-03.zip SHA256=21d47d7deb9582046c22786b676b9de869d4b00772c06c3a438d37ef57e3ca28`.
- Daily child: `BTCUSDT-15m-2018-03-04.zip SHA256=e466638b5103fd169f4976807db249215d120326172c0567e56280d16756408f; sidecar SHA256=a0243bd96bd70810e1e78b8b3190ce0b2806e62f30a3e97af6456be3f2cc93f7`.
- Daily parent: `BTCUSDT-30m-2018-03-04.zip SHA256=bb5f675d503f56204aed373916285bba018807e4e370e785a36a8823ba77475f; sidecar SHA256=350720744c5204eb0a3d5d37cadfb2bd651c018ea5fd7b9554e4b8b2e51b04fd`.
- Frozen monthly mismatch fields: `volume`; primary fields: `volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-10-15m-30m-2018-06-20T03:30:00Z
- Bucket: `2018-06-20T03:30:00Z`; relationship: `15m → 30m`; row evidence records: 6.
- Monthly child: `BTCUSDT-15m-2018-06.zip SHA256=a80442581d5ac478c283158bc754b62c90cb45bac2081126b2a5f3400ddd74bc`.
- Monthly parent: `BTCUSDT-30m-2018-06.zip SHA256=cd72295e0b4806803e08b9af1ab3580f420d1ac7a29b62e6f827c6e35ded7dcf`.
- Daily child: `BTCUSDT-15m-2018-06-20.zip SHA256=e9e1bbf1f0ee6c58bb0ca82eb1dd9f3b8e7b1edef4fe00058a30155c313213b9; sidecar SHA256=a92d14c392adfda255bb1259dac5cf0889cc609f32574f1055868500d62f0af0`.
- Daily parent: `BTCUSDT-30m-2018-06-20.zip SHA256=e4f01b5719589713d15c88faafb6eacaf6cb7812bea1c342ec96d83e0cbbeeaa; sidecar SHA256=323e110e100bc250c3538ef0fd2059ca10a54f5b9c73606a4364607d0e00f7cf`.
- Frozen monthly mismatch fields: `volume`; primary fields: `volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.

### AGG-11-30m-1h-2018-03-20T03:00:00Z
- Bucket: `2018-03-20T03:00:00Z`; relationship: `30m → 1h`; row evidence records: 6.
- Monthly child: `BTCUSDT-30m-2018-03.zip SHA256=21d47d7deb9582046c22786b676b9de869d4b00772c06c3a438d37ef57e3ca28`.
- Monthly parent: `BTCUSDT-1h-2018-03.zip SHA256=a3f45f20d28eab88292d1baac72402ebf59f4462d0bb834288f69b59a65cbf5f`.
- Daily child: `BTCUSDT-30m-2018-03-20.zip SHA256=862a652e1550c2e3286a40a3f24fee234b1c895cb08cb811ad48ab1daf5006cf; sidecar SHA256=f1b11f618a23f940ef887109a9d71200ba10094ec00d358ea5af315e396a0263`.
- Daily parent: `BTCUSDT-1h-2018-03-20.zip SHA256=5ef465a9737e8517291b314386f61086161aab1b7d2886ae8b4bb2ad9db5f1fe; sidecar SHA256=d0905ed32738107ab7409e1471517ed96e7e3e64af0c2199d2e486ee46942e9c`.
- Frozen monthly mismatch fields: `volume`; primary fields: `volume`; monthly mismatch signature reproduced: `True`.
- Candidate relevance result: direct interval overlap with `MTF_BREAKOUT_4H_D1` = `False`. Current decision: No direct interval overlap with 4h/D1 comparator; relationship remains open under global gate.


## 5. Automatic decision

**Decision: KEEP ALL 11 CASES OPEN. Do not change G0.**

Reasoning:
1. Exact archive hashes and daily sidecar lineage are now cross-linked per case.
2. Daily roll-up arithmetic matches in all 11 cases, but the monthly mismatch signature remains in all 11.
3. The comparator's lack of direct 4h/D1 interval overlap does not resolve the global source-authority question or prove every actual signal/position/valuation dependency irrelevant.
4. The frozen rulebook requires unresolved material inputs to be adjudicated or handled under a properly authorized scope. No independent adjudication or separate scoped Policy B application record is established by these artifacts.
5. No missing value is inferred. No source precedence, timestamp correction, synthetic candle, replacement, or candidate promotion is authorized.

## 6. Gate state after this checkpoint

- Canonical historical source: `NONE`
- G0: `BLOCKED_GLOBAL`
- Aggregation source cases closed by this checkpoint: `0/11`
- Policy B: `SENSITIVITY_ONLY; NOT AUTHORIZED FOR APPLICATION`
- G2: `FAIL_CURRENT_23_CANDIDATES`
- G3: `BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT`
- Profitability: `NOT ESTABLISHED`
- Production candidate build / acceptance-grade market backtest: `BLOCKED`
- Live signing / public broadcast / exchange orders: `BLOCKED`

## 7. Next decision-changing requirement

The next action that can actually change G0 is either:
- admissible official, key-specific historical publication/version evidence that resolves source authority; or
- an authorized independent review with written case-specific adjudication, and a separate scoped application record before any Policy B quarantine is applied.

Until then, continue only with bounded dependency mapping and deterministic fail-closed verification. This checkpoint improves traceability but does not itself close G0.
