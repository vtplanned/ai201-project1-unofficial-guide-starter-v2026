# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

This is a question-answering system over `campus_life`, a corpus of 88 short
posts in which students pass on the things nobody puts in the handbook: how
long the queue at a particular dining hall gets at 12:30, which residence hall
stays loud until 1am, how late you can still declare a course pass/fail. You
ask a plain question and get back an answer drawn only from those posts, with
the file it came from named underneath.

The corpus covers four areas — administrative deadlines and policies, nine
courses, seven residence halls, and seven dining halls — so it answers
questions like "are CS 210 midterms curved?" or "how much printing do I get per
semester?". Questions it has no documents for are refused before the model is
ever called, rather than answered from the model's general knowledge.

## Chunking Strategy

**Chunk size:** 450 characters — a ceiling, not a target. Chunks actually average 251 (shortest 141, longest 421).
**Overlap:** 0 characters of body text. Each document's title line is repeated on every chunk instead.

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

The starter's 800-character window never fired on this corpus. The longest
document in `campus_life` is 549 characters and the median is 305, so all 88
documents came out as 88 chunks — the chunker was doing nothing at all. That
was the baseline.

Splitting on paragraph breaks was the obvious fix, and on its own it would have
made retrieval worse. Every document opens with a one-line title, and the thing
being described is named *only* there:

```
Noise levels in Morrow House           the only mention of "Morrow House"

Loud until about 1am on weekends, no enforced quiet hours.

If you're someone who needs quiet to work, the library is open until 2am...
```

Split that on paragraphs and the last chunk is an anonymous sentence about the
library, no longer retrievable by anyone asking about Morrow House. Over half
the corpus has this shape; all 27 course files and all 21 housing files — so
it was not an edge case.

So each chunk gets its document's title line prepended. That is what the
overlap is doing: repeating ~30 characters of title carries the context that
matters, where 120 characters of arbitrary preceding prose would not.

**The ceiling changed partway through.** It was set to 400 first. At 400 the
ceiling collided with the merge step on `dining_verrill_street_grill.txt`: the
two body paragraphs merge to 387 characters, the title takes the room down to
378, and the result was re-split so that "Costs declining balance, or cash
after 11:00pm." became a 69-character chunk of its own. Sweeping the value
showed 450 is the smallest ceiling where nothing falls below the 120-character
floor, and that 450, 500 and 600 produce identical output. 450 is therefore the
smallest ceiling that never cuts a paragraph group this corpus actually
contains.

**What it still gets wrong.** The 120-character floor stops fragments but does
not give one topic per chunk. Three of the five sample chunks below cover two
topics — chunk 4 is wait times *and* seating, chunk 5 is noise levels *and*
where people go to study. Someone asking how many seats The Ridgeway Café has
gets a chunk that is mostly about lunch queues. Fragments were traded for a
milder version of the opposite problem, which is what acceptance criterion 4
now targets.

| | Before (`fallback_split`) | After (`split_documents`) |
|---|---|---|
| Chunks | 88 | 114 |
| Average length | 317 | 251 |
| Shortest | 178 | 141 |
| Longest | 549 | 421 |

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer
window — through the end of week six — but a drop after week two shows as a W
on your transcript. Nothing anywhere on the registrar's site says this plainly,
and students find out from each other.
```

**Chunk 2** — source: `course_cs_210.txt#0` — produced by: `chunker.py::split_documents`

```
CS 210 Data Structures

I'm a junior and I've done this twice now. Format is lecture with weekly labs;
slides go up after class, not before. Assessment: two midterms and a final, all
drawn from lecture material rather than the textbook. Midterms are curved, the
final is not.
```

**Chunk 3** — source: `course_math_220_exams.txt#0` — produced by: `chunker.py::split_documents`

```
MATH 220 Linear Algebra — assessment

Two midterms and a cumulative final. Curved to a b- median.

The problem sets are the course; the lectures make sense afterwards rather than
during.
```

**Chunk 4** — source: `dining_the_ridgeway_cafe_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: The Ridgeway Café

Adding to what people have said about The Ridgeway Café. The wait figure of 10
to 15 minutes at 12:30 matches what I've seen. If you're trying to eat between
classes, go before 11:45 and it's a different building entirely.

Also worth saying: seating is tight; about 40 seats for a building of 900.
Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall_noise.txt#0` — produced by: `chunker.py::split_documents`

```
Noise levels in Innisfree Hall

Asked about this a lot so writing it down. Moderate; the building is l-shaped
and the short wing is much quieter.

If you're someone who needs quiet to work, the library is open until 2am during
term and that's what most people in this building end up doing.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** Are CS 210 midterms curved?

**Answer:**

```
  (best distance 0.424, cutoff 0.6)

Yes, CS 210 midterms are curved.

Source: course_cs_210_exams.txt (and course_cs_210.txt)

Sources retrieved: course_cs_210.txt, course_cs_210_exams.txt, course_cs_340.txt,
course_phys_130.txt, course_phys_130_exams.txt
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
| What are the wait times at Kestrel Commons during lunch? | yes | 0.173 |
| How late can I declare a course pass/fail? | yes | 0.207 |
| How much printing does each student get per semester? | yes | 0.275 |
| How late does it stay loud in Morrow House on weekends? | yes | 0.292 |
| Are CS 210 midterms curved? | yes | 0.424 |
| What is the capital of Mongolia? | no | 0.825 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.848 |
| How do I write a for loop in Rust? | no | 0.877 |
| Who won the 1994 World Cup? | no | 0.886 |
| How do I change the oil in a diesel engine? | no | 0.934 |

In-corpus questions landed between **0.173 and 0.424**. Out-of-corpus questions
landed between **0.825 and 0.934**. The gap between the two groups is 0.401
wide with nothing in it, so any cutoff from roughly 0.45 to 0.80 behaves
identically on these ten questions.

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1. Pressure-testing my acceptance criteria.**  I drafted criterion 4 myself —
at least 3 of 5 sampled chunks covering exactly one topic — after reading my five chunks and counting 2 that were single-topic. I asked Claude to tell me how it would test my sentence using only what the sentence said, without suggesting improvements. It could not: my pass test described the failure ("some chunks can answer multiple questions") rather than the pass condition, so anyone following it would have counted backwards. I rewrote it as a pass condition. It also pointed out that I had named a target of 3 of 5 without saying which 5 chunks get sampled, so a grader reading different chunks could get a different count. I added the sampling method. The number and the reason were mine both times; what changed was the wording that made them checkable.

**2. Choosing a chunking strategy.** I described what I had seen in the
documents and asked for options rather than an implementation. Claude gave me
three: leave one post as one chunk, split on paragraph breaks, or split on
paragraph breaks and prepend each document's title line to every chunk.  I picked the third option. because the title is the only place the subject is named and
plain paragraph splitting would have stranded context in over half the corpus.



<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Sampled chunks cover exactly one topic | 3 of 5 | 2/5 | 2/5 | 2/5 | MISSED |
| 5. Named source is the file that holds the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Source file: `results/run_2026-09-29_0019_before.md`, produced by
`run_eval.py::main`. Retrieval by `store.py::search` over chunks from
`chunker.py::split_documents`. Criterion 4 is measured on chunks rather than on
answers, by reading the five printed by `app.py chunks -n 5`, so it does not
vary between runs; criterion 3 is one deterministic pass for the same reason.

**Real output — criteria 1, 2 and 5** (run 1, `run_eval.py::main`):

```
### What are the wait times at Kestrel Commons during lunch? — run 1

- Best distance: 0.1729 (passed the gate)
- Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt,
  dining_kestrel_commons_followup.txt, dining_north_kitchen_followup.txt,
  dining_the_ridgeway_cafe_followup.txt

At Kestrel Commons, the wait times during lunch are 20 to 25 minutes between
12:15 and 1:00, and under 5 minutes before 11:45.

Source: `dining_kestrel_commons.txt`
```

That one line carries all three: the retrieved chunks contained the answer
(criterion 1), a source is named (criterion 2), and `dining_kestrel_commons.txt`
genuinely contains "20 to 25 minutes between 12:15 and 1:00, under 5 minutes
before 11:45" rather than a sibling that merely mentions Kestrel Commons
(criterion 5).

**Real output — criterion 3** (`run_eval.py::check_out_of_scope`, cutoff 0.6):

```
| Out-of-scope question                        | Best distance | Gate    |
| What is the capital of Mongolia?             | 0.825         | refused |
| How do I change the oil in a diesel engine?  | 0.934         | refused |
| Who won the 1994 World Cup?                  | 0.886         | refused |
| What is the recommended dosage of ibuprofen? | 0.848         | refused |
| How do I write a for loop in Rust?           | 0.877         | refused |
-> gate refused 5 of 5
```

**Real output — criterion 4** (`app.py chunks -n 5`, produced by
`chunker.py::split_documents`). Two of the five covered one topic; this is the
kind that did not:

```
Re: The Ridgeway Café

Adding to what people have said about The Ridgeway Café. The wait figure of 10
to 15 minutes at 12:30 matches what I've seen. If you're trying to eat between
classes, go before 11:45 and it's a different building entirely.

Also worth saying: seating is tight; about 40 seats for a building of 900.
Nobody tells you this at orientation.
```

Wait times and seating capacity are two separate questions in one chunk.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks include one containing the answer, 4 of 5 | **MET** | All five questions returned the answer in a retrieved chunk on all three runs, so 5/5 clears 4 of 5 with a question to spare. Not close. |
| 2 | Every answer names a source, 5 of 5 | **MET** | All 15 answers named a file. The format varied between runs — "Source: x", "(x)", "from `x`" — but I set the target on a source being named, not on its formatting, so varied wording does not make it a miss. |
| 3 | Gate refuses out-of-corpus questions, 4 of 5 | **MET** | All five out-of-corpus questions were refused, the closest at 0.825 against a 0.6 cutoff. One deterministic pass, so the same 5/5 goes in all three columns. |
| 4 | Sampled chunks cover exactly one topic, 3 of 5 | **MISSED** | Only 2 of the 5 sampled chunks answered a single question. The other three each covered two — wait times *and* seating, noise levels *and* where to study. 2 is below 3, so it misses. See the note below on whether the count is even stable. |
| 5 | The named source is the file that holds the answer, 4 of 5 | **MET** | I opened every cited file and checked the answer text was in it. All 15 citations were correct, including both CS 210 siblings, where `course_cs_210.txt` and `course_cs_210_exams.txt` both genuinely state the midterms are curved. |

**A note on criterion 4's measurement.** Applying my own test — "counting the
distinct questions it could answer" — to the two chunks I scored as passing,
I am not confident they pass either. The add/drop chunk answers when you can
add, when you can drop, and when a W appears on your transcript. On a strict
reading the before-count is 0 of 5, not 2 of 5. The verdict is MISSED on any
reading, so this does not change the outcome, but the number underneath it is
not reproducible. That is a measurement problem rather than a result problem,
and it is recorded as a revision under criterion 4 in `criteria.md` rather
than being edited into the original.

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

**Criterion 4 — stage: chunking. Mechanism: the merge step combines on length
and never looks at meaning.**

`chunker.py::_merge_short` walks the paragraphs of a document and keeps gluing
them together until the buffer reaches `MIN_BODY_CHARS`, which was 120. Its only
input is a character count. Nothing in it asks whether the two paragraphs it is
about to join are about the same thing.

On this corpus that guarantees the failure, because the documents are built as
a short lead paragraph plus a short unrelated afterthought. In
`dining_the_ridgeway_cafe_followup.txt` the first paragraph is wait times at
12:30 and the second is that seating is tight — 40 seats for a building of 900.
Neither reaches 120 characters on its own, so the merge joins them, and the
result answers two questions instead of one. The same pattern produced the
noise-plus-library chunk in `housing_innisfree_hall_noise.txt` and the
exams-plus-problem-sets chunk in `course_math_220_exams.txt`.

**The pattern across the miss.** All three failing chunks came from documents
whose paragraphs are individually shorter than the floor. It is one problem,
not three: the floor was set to stop fragments, and on documents this short the
only way it can do that is by joining paragraphs that have nothing to do with
each other. Criterion 4's own reason predicted exactly this trade-off before
the test was run.

The four criteria that were met are untouched by it: the merge affects what
sits inside a chunk, not whether the chunk is retrieved or cited.

## The Improvement

**What I changed:** `MIN_BODY_CHARS` in `chunker.py` from 120 to 0, which stops
`_merge_short` merging anything. Every body paragraph now becomes its own chunk,
with the document's title line still prepended. One change, one constant; the
rest of the pipeline is untouched. The corpus went from 114 chunks to 183, and
average chunk length from 251 characters to 167.

**Why I picked it:** the diagnosis names the merge step as the mechanism that
puts two topics in one chunk, so removing the merge is the narrowest change that
addresses it. It also deliberately reverses the trade-off I wrote into criterion
4's reason last unit — "I can't have no fragments and one topic per chunk at the
same time, and I chose no fragments" — so this unit measures what the other
choice costs.

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Sampled chunks cover exactly one topic | 3 of 5 | 3/5 | 3/5 | 3/5 | MET |
| 5. Named source is the file that holds the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Source file: `results/run_2026-09-29_0111_after.md`, same functions as before.

**Real output after the change** (`app.py chunks -n 5`, produced by
`chunker.py::split_documents`) — the sampled chunks that now pass:

```
CS 340 Databases — assessment
Start the term project in week three, not week eight; everyone learns this the
hard way.
```
```
Workload for PHYS 130 Mechanics
People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time,
not optimistic time.
```
```
Re: Verrill Street Grill
Also worth saying: one register, so the queue is a single line no matter how
busy. Nobody tells you this at orientation.
```

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

Yes, on the criterion it was aimed at, and it cost nothing measurable
elsewhere.

| Criterion | Target | Before | After |
|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 |
| 4. Sampled chunks cover exactly one topic | 3 of 5 | **2/5 MISSED** | **3/5 MET** |
| 5. Named source is the file that holds the answer | 4 of 5 | 5/5 | 5/5 |

Criterion 4 went from 2 of 5 to 3 of 5 and crossed its target. Three of the
five sampled chunks now answer exactly one question each — the CS 340 project
advice, the PHYS 130 workload figure, the Verrill Street Grill register — where
before those paragraphs would have been merged into whatever sat next to them.

Retrieval also got slightly *better* rather than worse, which I did not expect.
Best distances moved from 0.292 to 0.208 on the Morrow House question and 0.173
to 0.161 on Kestrel Commons, presumably because a chunk that contains only the
relevant paragraph is a closer match than one padded with an unrelated one. CS
210 moved the other way, 0.424 to 0.448. All ten distances stayed on the correct
side of the 0.6 cutoff and the gate still refused 5 of 5, so the change did not
buy criterion 4 at the expense of criterion 3.

I expected a trade-off and did not get one. The honest reading is that the
120-character floor was protecting against a problem this corpus does not
really have at retrieval time — the fragments it prevented were not hurting the
four criteria I could measure.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

No criterion is still missed after the fix, so what follows is what I know is
wrong that my criteria did not catch.

**Criterion 4's measurement, which is the real problem.** It reads 3 of 5 now,
but I cannot reproduce that number reliably. "Counting the distinct questions a
chunk could answer" is a judgement, and I reached different counts on the same
chunks an hour apart — the add/drop chunk is either one topic (deadlines) or
three (adding, dropping, the W), depending on how finely I read it. I would
replace the judgement with something mechanical: a chunk passes if it came from
exactly one source paragraph. That is checkable by anyone, needs no
interpretation, and on the current chunker every chunk would pass it — which
tells me the real criterion I want is about the *documents*, not the chunks.
I stopped here because rewriting the criterion properly means rewriting what it
measures, and I would rather do that deliberately than at 1am.

**The sample is 5 chunks out of 183.** Criterion 4 judges under 3% of the
corpus, and `app.py chunks -n 5` picks a different five each time it is asked.
A number that moves when you re-sample is not a measurement. Fix: fix the five
by name, or score all 183 with a rule cheap enough to apply automatically.

**Fragments came back and nothing is watching them.** The shortest chunk went
from 141 characters to 63, because removing the merge removed the only floor
in the chunker. None of my five criteria mentions chunk length, so this change
could have flooded the index with two-word chunks and every criterion would
still have read MET. That is a gap in my criteria, not in the pipeline. I would
add a sixth: no chunk shorter than N characters, with N measured rather than
guessed.

**The add/drop chunk still covers three questions** and no change to the merge
step will fix it, because it is one paragraph in the source document. Splitting
it means splitting *within* a paragraph, which is a different and harder change
than the one I made, and it is the reason criterion 4 sits at 3 of 5 rather
than 5 of 5.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

**Criterion 4, and not because I missed it.** I missed it on purpose and that
part worked — it was the only criterion with anything to diagnose, and the
whole improvement came out of it. What I would change is that I wrote a target
on a property I had no reliable way to count. "Covers exactly one topic" sounds
measurable and is not: it depends on how finely the reader chooses to slice a
question. I would keep the intent and swap the test for something mechanical,
along the lines of "no chunk is built from more than one source paragraph."
Worth noting that the version I filed already tried to fix this by adding "I
judge this by reading each sampled chunk and counting the distinct questions it
could answer" — that made the method explicit without making it reproducible,
which I did not realise until I had to apply it twice.

**Criteria 1, 2, 3 and 5 were too safe, and the numbers say so.** All four came
in at 5/5 on the first run, three of them against targets of 4 of 5. Nothing
about them was hard, and a criterion you clear without noticing teaches you
nothing. Specifically:

- **Criterion 3** is the worst offender. My out-of-corpus questions were about
  Mongolia, diesel engines, the World Cup, ibuprofen and Rust — nothing remotely
  like a campus question, and they landed at 0.825–0.934 against a 0.6 cutoff.
  A real test would use questions that sound like they belong: "what are the
  wait times at the gym?" or "how do I appeal a parking ticket?" — plausible
  campus questions my corpus happens not to cover. I would tighten it to **5 of
  5 refused on plausible-but-uncovered questions** and expect to miss it.
- **Criterion 1** I would raise from 4 of 5 to 5 of 5. I set it at 4 expecting
  the sibling-file structure to cost me one question, and it never did.

The general lesson: I set the targets I could defend rather than the ones that
would tell me something. The one criterion where I deliberately targeted a
property I was already failing is the one that produced every point of this
unit's work.
