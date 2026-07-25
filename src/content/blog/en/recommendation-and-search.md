---
title: "Recommendation and semantic search for a content app"
description: "The four layers of a multimodal recommender: from raw content analysis to vector representations, hybrid retrieval, and multi-source ranking."
lang: "en"
order: 1
field: "REC"
topics: ["recommender systems", "semantic search", "embeddings", "collaborative filtering", "ANN"]
---

A music app has to keep answering two questions: what should this person listen to next, and what comes back when they type something into the search box. They look like two separate features, but they share most of the machinery underneath — and that shared machinery is what this post is mostly about.

## The system as built

<figure class="diagram">
<svg viewBox="0 0 640 250" role="img" aria-label="The four layers of the recommender, a one-way dependency chain from raw content to ranking">
  <defs><marker id="rec-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">INPUTS</text>
    <text class="lbl" x="176" y="14" font-size="9.5">LAYERS 1 AND 2</text>
    <text class="lbl" x="404" y="14" font-size="9.5">LAYERS 3 AND 4</text>
  </g>
  <rect class="box" x="0" y="28" width="150" height="40"/>
  <rect class="box" x="0" y="88" width="150" height="40"/>
  <rect class="box" x="0" y="148" width="150" height="40"/>
  <rect class="box" x="176" y="28" width="196" height="40"/>
  <rect class="box-accent" x="176" y="88" width="196" height="54"/>
  <rect class="box" x="176" y="162" width="196" height="40"/>
  <rect class="box" x="404" y="54" width="182" height="46"/>
  <rect class="box" x="404" y="134" width="182" height="46"/>
  <g class="flow" marker-end="url(#rec-a)">
    <path d="M150 48 H172"/><path d="M150 108 H172"/><path d="M150 168 H172"/>
    <path d="M274 68 V84"/><path d="M274 142 V158"/>
    <path d="M372 108 H390 V80 H400"/><path d="M372 122 H390 V156 H400"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="46">Audio files</text>
    <text x="10" y="60" font-size="10" class="dim">raw content</text>
    <text x="10" y="106">Metadata and lyrics</text>
    <text x="10" y="120" font-size="10" class="dim">title, artist, lyrics</text>
    <text x="10" y="166">Interactions</text>
    <text x="10" y="180" font-size="10" class="dim">plays, likes, skips</text>
    <text x="186" y="46">1. Content analysis</text>
    <text x="186" y="60" font-size="10" class="dim">five groups of descriptive tags</text>
    <text x="186" y="106">2. Embedding and indexing</text>
    <text x="186" y="120" font-size="10" class="dim">four vector spaces</text>
    <text x="186" y="134" font-size="10" class="dim">four nearest-neighbor indexes</text>
    <text x="186" y="180">Collaborative and sequence</text>
    <text x="186" y="194" font-size="10" class="dim">models trained offline</text>
    <text x="414" y="74">3. Hybrid search</text>
    <text x="414" y="88" font-size="10" class="dim">vector plus keyword branches</text>
    <text x="414" y="154">4. Multi-source ranking</text>
    <text x="414" y="168" font-size="10" class="dim">content, collaborative, sequence</text>
  </g>
</svg>
<figcaption>Four layers, one-way dependencies. The representation layer is the bottleneck: the last two layers only read the indexes it produces.</figcaption>
</figure>

The architecture is four modules arranged in a one-way dependency chain, running as a separate service alongside the business backend.

### Layer one: content analysis

The input is a raw audio file. The output is a set of descriptive tags in five groups: genre, mood, instrumentation, vocal characteristics, and language.

What matters at this layer is that **the tag taxonomy was not invented from scratch**. Each group is anchored to an existing classification scheme. Mood follows Russell's circumplex model of affect, which splits the plane into four quadrants along an arousal axis and a valence axis. Instrumentation follows Hornbostel–Sachs, which groups instruments by the mechanism that produces the sound: chordophones, aerophones, membranophones, idiophones, and electrophones. Language uses a subset of an off-the-shelf language identifier's label set, chosen so it lines up with the model used downstream.

Anchoring to an existing scheme sounds like a small detail, but it is what determines whether the label set can grow: when a new tag is needed, there is a structure telling you where it belongs, instead of a flat list anyone can append to at will.

On the model side, this layer runs two networks in parallel. One is a multi-label classifier built on a transformer architecture for audio spectrograms, with four separate heads for the first four tag groups. The other is a dedicated language identification network built on an architecture common in speech processing. Splitting the two rather than folding them into one multi-head network was deliberate: language identification keys off phonetic cues while genre classification keys off harmonic and rhythmic ones, and forcing them to share a trunk tends to make the two tasks pull against each other.

### Layer two: representations and indexing

This is the bottleneck of the whole system. Every track becomes four vectors living in four different spaces:

- **An audio vector**, taken from the hidden states of the spectrogram network and averaged over the time axis.
- **A tag vector**, produced by a multilingual text embedding model. The interesting part: rather than encoding the tags as a binary vector, the system **stitches them into a natural Vietnamese sentence** — roughly "Title X. Artist Y. Genre A. Mood B. Instruments C" — and embeds that. A query like "sad songs with guitar" then matches content without any hand-written dictionary mapping keywords to tags.
- **A lyrics vector**, from the same text embedding model, run over the lyrics.
- **A behavior vector**, read off the factor matrices of the collaborative filtering model.

Each of the four gets its own index, built with an approximate nearest neighbor library over a hierarchical graph structure. The idea is a stack of graph layers: sparse at the top so a search can take long jumps, dense at the bottom so it can refine — which makes search time grow logarithmically rather than linearly with the number of items.

### Layer three: hybrid search

A query runs down two branches in parallel. The vector branch embeds the query into the same space as the content and looks for neighbors. The keyword branch does string matching against titles, artist names, and tags. The two branches produce two lists, and a fusion step merges them together with two secondary factors, popularity and recency.

Queries can be text or a clip of audio; the latter goes straight into the audio vector index.

### Layer four: multi-source recommendation

Three candidate sources run independently and are then merged.

**Content-based.** Average the vectors of the tracks a user has liked to get a taste profile, then look for that profile's neighbors. For a new user who has liked nothing yet, the profile is built from the most popular tracks — a cheap and simple cold-start fallback.

**Collaborative filtering.** Alternating least squares over the interaction matrix. The idea is to factor the user-by-item matrix into two smaller factor matrices, then alternately hold one side fixed and solve for the other — each step is a least squares problem with a closed-form solution, so it converges quickly and parallelizes well.

**Sequential.** A transformer takes the sequence of items a user has just consumed and predicts the next one, with a causal mask so each position can only look backwards.

All three have the same shape: they return candidates with scores, and a linear fusion function combines them into the final ranking, again with popularity and recency added on top.

### Implicit signals: turning behavior into numbers

One design detail here is worth carrying elsewhere. The raw interaction data is nothing but discrete events — play, like, unlike. Before any of it reaches a model, each event is converted into a real-valued weight by a handful of rules:

- An early skip — barely any of the track played before moving on — carries a **negative** value. It is evidence of dislike, not a neutral event.
- A near-complete listen gets a multiplier: a stronger positive signal than stopping halfway.
- An interaction the user sought out counts for more than one that arrived through a recommendation, because it reflects deliberate intent.
- Recent interactions weigh more than old ones, decaying over time.

Those four rules encode things a plain liked-or-not table cannot. This is the step that turns event data into a learnable signal, and it usually does more for quality than the choice of model does.

### Infrastructure

The AI service is Python with FastAPI, exposing four endpoints, one per module. The business backend, written in Java, calls into it. Data sits in a document database, with a cache layer in front of recommendation and search results. Model weights are baked into the image at build time rather than downloaded at startup.

One operational detail worth recording: heavy jobs are split out into their own subprocess rather than run inside the web process. The models take a lot of memory, and sharing a process means one expensive request can take down the worker serving everyone else.

## Background: why this problem is hard

### The search space is too large to score directly

With a catalog of a few thousand items you can score every item for every user. With a few million you cannot. That constraint shapes the entire architecture of large systems, and it is the reason approximate nearest neighbor search exists: give up a small fraction of the correct results in exchange for an order-of-magnitude speedup.

### Three families of methods, three different strengths

**Content-based** methods work even for a brand-new item, because they only need features of the item itself. The downside is a tendency to circle around what is already known, which makes it hard to lead a user toward new tastes.

**Collaborative filtering** finds connections no content feature could explain — two tracks with nothing musical in common that the same group of people happens to love. In exchange it needs interaction history, so it fails on new items and new users.

**Sequential** methods capture intent within the current session, which the other two ignore: someone who has just played three lullabies is in a very different context from someone who has just played three gym tracks, even when their long-term profiles look identical.

None of the three substitutes for the others, which is why production systems are always hybrids.

### Cold start is a separate problem

A new item nobody has played gives collaborative filtering nothing to say about it. The same goes for a new user. The common responses: lean on content features for new items, on demographics for new users, or deliberately inject new items into a small slice of traffic to collect an initial signal.

## How the industry does this

Set against published writeups of large-scale system design, four things stand out.

**A funnel of stages.** Two or three stages is the common shape. Candidate generation is cheap and biased toward recall, usually several generators running in parallel under different criteria — relevance, popularity, freshness — then merged, taking millions of items down to a few hundred. Scoring is more expensive and feature-rich, cutting that to a few dozen. Re-ranking applies business rules: source diversity, filtering out already-seen content, injecting exploration, balancing the interests of both sides of a two-sided marketplace.

The staging is not only about speed. It also lets each part be improved independently, and lets you measure which stage is currently the bottleneck.

**Two model families for two stages.** Matrix factorization is fast and cheap but cannot use anything beyond identifiers. A two-tower network — one tower encoding the user, one encoding the item, both projecting into a shared space — accepts rich features and handles new users better, at a higher cost. The usual pairing is the light model at candidate generation and the heavy one at scoring.

**Offline metrics have to connect to real behavior.** Ranking metrics like nDCG account for position: a correct result at rank one is worth more than the same result at rank ten. Alongside them sit the online metrics — click-through rate, watch time, completion rate. What matters is picking the offline metric that predicts the online one the organization actually cares about.

One variant worth noting is normalized cross-entropy, which divides the model's loss by that of a baseline always predicting the average rate. A value above one means the model is worse than the baseline — the metric announces its own failures instead of leaving the reader to work them out.

**Cross-modal search needs a shared space.** For a text query to reach audio content, the two have to live in the same vector space, and that only happens when a model is trained contrastively on text-audio pairs. Placing two separate encoders side by side and adding their scores does not produce that capability — it only lets you compare text against the textual description of the content, which is exactly how the system above works.

## A few things to take away

**The event-to-signal step matters more than it looks.** The formula that turns interactions into weights — distinguishing a skip from a full listen, a self-directed play from a recommended one, recent from long ago — delivers more value per line of code than anything else in the system.

**Fusing scores from several sources means normalizing first.** Scores from three sources typically live on completely different scales: one is a similarity bounded in the unit interval, one is an unbounded dot product, one is a probability over thousands of classes and therefore always tiny. Adding them with weights as-is means the small-scale source contributes almost nothing, however large its nominal weight. Normalizing onto a common scale, or fusing by rank instead, is not optional.

**The distance metric has to match how the vectors were produced.** Nearest neighbor indexes default to Euclidean distance, while most semantic representations are designed to be compared by cosine. Without normalizing vector length before indexing, ranking ends up driven by magnitude rather than direction alone.

**Build the representation layer before anything else.** Of the four layers, the last three all read indexes produced by layer two. Rebuilding a system like this, that ordering is forced — and it is also where investment pays off most, because representation quality sets a ceiling on everything downstream.
