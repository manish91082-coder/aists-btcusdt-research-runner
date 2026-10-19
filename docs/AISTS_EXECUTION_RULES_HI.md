# AISTS Execution Rules: Permanent Operating Lock (Hindi)

स्थिति: इस repository की execution policy. हर काम के पहले इसे GitHub से पढ़ना अनिवार्य है.
Canonical repository: https://github.com/manish91082-coder/aists-btcusdt-research-runner
Active research branch: cp-0165-4h-archive-audit
Canonical base/main must not be changed except through an explicitly reviewed and authorized merge.

## हर response / हर execution का अनिवार्य क्रम
1. INSPECT: इस नियम-फ़ाइल, live branch/HEAD, main HEAD, relevant roadmap/checkpoint, PR state और latest applicable CI terminal result को GitHub से पढ़ो.
2. VERIFY: hashes, branch, exact commit, workflow run conclusion, files and gates cross-check करो. Queued/in-progress को PASS मत कहो. पुराने run को नए SHA का test मत बताओ.
3. DECIDE: एक ही highest-value atomic next task चुनो. पहले स्पष्ट करो कि वह कौन-सा वास्तविक blocker हटाएगा या कौन-सा आवश्यक evidence देगा.
4. IMPLEMENT: सिर्फ उसी bounded task को लागू करो. Append-only evidence; अनावश्यक checkpoint, status-only commit, repeated scans या cosmetic churn नहीं.
5. TEST: बदलाव के अनुरूप targeted tests और applicable workflow चलाओ. Failures छिपाओ मत.
6. PUSH: केवल अनुमत feature branch पर push/commit; secrets, live keys या credentials कभी नहीं.
7. RECONCILE: GitHub से नया HEAD, main HEAD, PR status, changed files और CI result दोबारा पढ़कर verify करो.
8. CHECKPOINT: roadmap में meaningful verified change append करो. File/commit/run IDs तभी लिखो जब live GitHub से प्रमाणित हों.
9. NEXT: उसी जवाब के अंत में अगला एक ठोस कदम और मिशन की वर्तमान बाधा बताओ. अगला उत्तर शुरू करने से पहले फिर से इस फ़ाइल और live GitHub state को पढ़ो.

## Goal lock
मुख्य लक्ष्य BTCUSDT Spot research के लिए विश्वसनीय, reproducible, cost-aware, risk-adjusted net-profit validation तक पहुँचना है. प्रारम्भिक पूँजी ₹10,000 को USDT में परिवर्तित मानकर fees सहित evaluate करना है; Binance primary exchange और BNB fee treatment को evidence से जाँचना है. प्राथमिक research timeframe 4h है. Binance public downloadable archives प्राथमिक data source हैं; live REST market-data pulls से archive evidence को replace नहीं करना.

## Current hard gates (इनको अनुमान से clear नहीं करना)
- Canonical historical source = NONE until admissible evidence establishes it.
- G0 = BLOCKED_GLOBAL.
- G3 = BLOCKED_PARTIAL_MATERIAL_QUARANTINE_EFFECT.
- 23 historical candidates remain G2 FAIL.
- Profitability = NOT ESTABLISHED.
- Production candidate build / market backtest remain blocked while source and frozen-policy gates are unresolved.
- Policy B is sensitivity-only unless an actually authorized independent review and a separate scoped application record explicitly authorize application.
- No fabricated candles, inferred fills, silent timestamp shifts, invented source provenance, invented approvals, or unsupported performance claims.
- Live signing, public broadcast and exchange orders are permanently BLOCKED unless the user explicitly changes the project safety policy; never infer authorization from CI or a research result.

## Anti-loop / anti-drift rules
- Do not repeat a checksum, archive, child-interval, or source scan already marked exhausted unless genuinely new evidence or a changed input justifies it.
- Repeated green CI is not market evidence, provenance, strategy approval, or profitability.
- Do not create a commit merely to look busy. Every change must remove a blocker, improve a required safety invariant, or add decision-changing evidence.
- Distinguish static tests, synthetic fixtures, source-code inspection, archive audit, market backtest, independent review, and live trading; they are not interchangeable.
- If a tool fails or the current state cannot be verified, state that explicitly and do not claim completion.
- Never post to a third-party issue or request/claim independent approval without authority.
- Keep PR #2 (CP-0120 AI brain foundation) separate from PR #3 (CP-0165 archive audit); do not merge either simply to make progress. Inspect actual conflict/check state first.

## Every response format
1. What GitHub rule/state was reread and what was verified this turn.
2. One completed goal-directed action, or explicitly why a safe action is blocked.
3. Evidence: exact file/commit/CI/PR identifiers only when verified.
4. Next single atomic action.
5. Mission Navigation: current gate, next blocker, and distance-to-goal described without fabricated percentage.

This is a durable repository instruction, not a claim that GitHub repository settings or branch protection have been technically locked. Enforce it by rereading and following it each turn.

## Solution-first responsibility lock (user-directed)
- समस्या दिखते ही केवल blocker का वर्णन करके रुकना, panic बढ़ाना, या वही जाँच दोहराना स्वीकार्य नहीं है. पहले लक्ष्य और hard gates को स्थिर रखकर कम-से-कम एक व्यावहारिक, कम-जोखिम वाला workaround / alternate execution path स्वयं खोजो.
- हर blocker पर क्रम से तय करो: (1) क्या मौजूदा evidence से सुरक्षित काम आगे बढ़ सकता है, (2) क्या local/repository/CI या बिना-account public data route उपलब्ध है, (3) क्या task को exploratory-only बनाकर उपयोगी analysis किया जा सकता है, (4) क्या exact missing dependency वास्तव में user input माँगती है. केवल अंतिम स्थिति में user से input माँगो.
- अगर preferred route बंद हो, तो निकटतम goal-aligned विकल्प पर आगे बढ़ो; blocker को साफ बताओ, लेकिन उसी को पूरी प्रगति का अंत मत बनाओ. विकल्पों की बार-बार सूची बनाने के बजाय एक सर्वश्रेष्ठ अगला कदम चुनकर execute और verify करो.
- हर response में मिशन से alignment, वास्तविक progress, और अगला सबसे उपयोगी कदम जाँचो. Progress claim केवल किए गए और सत्यापित काम पर आधारित हो; status-only commits, panic language, fabricated success, repeated scans और scope drift नहीं.
- User-directed exploratory/non-acceptance-grade analysis or backtesting may proceed on available datasets with explicit provisional labels, separate source results, fee-aware assumptions, and leakage-safe chronological splits. This permission does NOT clear G0, change the frozen CP0040 acceptance rulebook, authorize candidate promotion, establish profitability, authorize source merging, or permit live signing/broadcast/orders. Acceptance-grade validation remains blocked until its frozen gates are actually satisfied.
- This operating lock is durable in the repository policy and must be reread/enforced each execution. It is not a claim that account-level ChatGPT Memory or GitHub branch protection has been technically changed.
