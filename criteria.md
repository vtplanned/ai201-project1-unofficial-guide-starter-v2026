# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

4 of 5 rather than 5 of 5 because my corpus stores each course and each
residence hall across three sibling files — main, exams and workload for
courses; main, laundry and noise for housing. Several of those files mention
the same course or building, so the chunk that actually holds the answer
competes with two near-identical neighbours. "Are CS 210 midterms curved?" has
three plausible files behind it and only one right one, and I expected at least
one of my five questions to land on a sibling.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

All five and not four because naming the file is not a judgement call — it is
an instruction the pipeline already sends on every request. `GROUNDING_INSTRUCTION`
in `generate.py` requires the answer to name the document it came from, and the
gate means the model is only ever called when a chunk came back close enough to
cite. A missing source would mean the instruction was ignored outright, which
is a broken pipeline rather than a hard question, so there is no reason to
allow one failure.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

The two groups separated cleanly when I measured them in Milestone 4. My five
in-corpus questions had best distances between 0.173 and 0.424; the five
out-of-corpus questions landed between 0.825 and 0.934. That leaves a 0.401-wide
gap with nothing in it, and the 0.6 cutoff sits inside it with room on both
sides. I kept 4 of 5 rather than raising it to 5 of 5 because the gap was
measured on exactly these five out-of-corpus questions, and a different
off-topic question could land closer than any of them did — the nearest one
already retrieved a history-course file at 0.825, which suggests the corpus has
some pull on general-knowledge questions.

---

## 4. Something about your chunks

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

At least 3 of 5 sampled chunks cover exactly one topic, meaning a chunk passes if it answers only one question. I judge this by reading each sampled chunk and counting the distinct questions it could answer.


**Why this target:**

When I read 5 chunks I counted 2 that were single-topic. I picked 3 because
my chunker decides what to merge using only paragraph length, and if it also looked at whether two paragraphs were about the same thing it could keep at
least one more pair apart. I didn't pick 4 or 5 because that would mean splitting nearly every paragraph into its own chunk, and those pieces would
fall below the 120-character floor I added to stop fragments. I can't have no fragments and one topic per chunk at the same time, and I chose no
fragments.

> **Revised in unit 2:** At least 3 of 5 sampled chunks are built from exactly
> one source paragraph.
>
> **Why revised:** The original could not be measured the same way twice.
> "Counting the distinct questions a chunk could answer" turned out to depend
> on how finely I chose to slice a question — the add/drop chunk is one topic
> (deadlines) or three (adding, dropping, the W on your transcript) depending
> on the reading, and I scored the same five chunks differently an hour apart.
> The verdict was MISSED on every reading, so this is not a target being
> lowered after the fact; the number behind it was never reproducible. Counting
> source paragraphs is mechanical and gives any reader the same answer.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->


For at least 4 of my 5 test questions, the source document named in the
answer is the document that actually contains the answer. I judge this by
opening the named file and checking that the answer text appears in it.

**Why this target:**

Criterion 2 only checks that a source is named, not that it is the correct one. My corpus splits each course and each building across three files —
main, exams, workload for courses; main, laundry, noise for housing — so five documents can all legitimately mention "CS 210" and only one of them
answers the question. Naming the wrong sibling file would look right and be wrong. I picked 4 of 5 rather than 5 of 5 because the retrieved chunks come
back ranked and the top chunk is not always the one the answer was drawn
from.




---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->

---

## Unit 9 acceptance criteria

Set up the local server using `RUNNING.md` and start it with
`AI201_CACHE=0 PORT=5055 python serve.py`. Send `Is the housing lottery random?`
to `/ask` with a 120-second timeout and wait for the answer to warm up the
embedding model. With no other traffic, run
`python capstone_eval.py --label before --trials 3`. Each trial sends three
in-corpus questions, two out-of-corpus questions, two invalid bodies, and one
health check. Read only the lines appended to `logs/requests.jsonl` during the
check you are scoring. Apply the per-trial targets to all three trials.

### 1. One log record per request

For each eight-request trial, parse the appended lines and require exactly
eight JSON objects with eight distinct `request_id` values. In order, their
`method` and `route` must match the seven `POST /ask` requests and one
`GET /health` request. The logged `question` values for the first five records
must match the five questions sent, in order.

I use this file to count traffic and calculate cost per request. The first
instrumented run left 11 records for 10 requests, so even one extra row can
skew those totals.

### 2. Required log fields

Open the JSON records for each trial and check that 8 of 8 contain `ts`,
`request_id`, `route`, `method`, `outcome`, `status`, `duration_ms`,
`model_calls`, `prompt_tokens`, and `output_tokens`. Each answered or refused
`/ask` record must also contain `question`, `answer_chars`, `refused`,
`best_distance`, and `sources`. The `/health` record must contain `index_ready`.

The cost calculation needs the counters even on requests that spend zero
tokens. The local run path also uses `index_ready` to tell whether the Chroma
index is available when Flask is already responding.

### 3. Invalid requests leave a log record

With the warm server idle, send two `POST /ask` requests with
`Content-Type: application/json`, first with body `{}` and then with body
`not json at all`. After each response, check that it returned HTTP 400 and
that exactly one new row has `outcome: "bad_request"`, `status: 400`, an empty
`question`, and `model_calls`, `prompt_tokens`, and `output_tokens` all set to
zero. Both requests must pass.

Both bodies take the early return in `serve.py`, before retrieval or model
generation. If either path skips the log, the caller sees a 400 that I cannot
account for in the request history.

### 4. Model-call counts under concurrent requests

With the same warm server and cache disabled, launch three `POST /ask`
requests together from separate clients. Use `What is the printing quota?`,
`How noisy is Aldridge Hall?`, and `When is the add drop deadline?`. Require
three HTTP 200 responses with `refused: false`, then match each response's
`request_id` to its log row. All 3 of 3 rows must show `model_calls: 1`.
If the server prints `service pushed back. Retrying` during the batch, repeat
after a minute so each answer can be measured on a single attempt.

Flask can handle overlapping requests while `generate.py` keeps module-global
counters. The first overlapping answers logged 3, 3, and 4 calls for one call
each. That would inflate my estimate of how many calls a day the guide uses.

### 5. Warm response latency

For each sequential trial, require all three in-corpus questions to have
`outcome: "answered"` and `status: 200`. Sort those three rows by
`duration_ms`. The middle value must be at most 1,500 ms and the largest at
most 2,500 ms.

The warm baseline had a roughly 911 ms median and a 2,420 ms maximum. These
bounds allow some variation in the model call and catch slower runs once the
local ONNX model has finished its 30–60 second startup load. Disabling the
response cache keeps its roughly 127 ms hits from pulling the median down.
