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

<figure class="diagram">
<svg viewBox="0 0 640 256" role="img" aria-label="Russell's circumplex: a plane of valence and arousal with eight example moods placed around the circle">
  <defs><marker id="rec-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <ellipse class="grid dashed" cx="320" cy="134" rx="190" ry="86"/>
  <g class="axis" marker-end="url(#rec-a2)">
    <path d="M320 134 V38"/><path d="M320 134 V230"/>
    <path d="M320 134 H90"/><path d="M320 134 H550"/>
  </g>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="320" y="26" text-anchor="middle">HIGH AROUSAL</text>
    <text class="lbl" x="320" y="248" text-anchor="middle">LOW AROUSAL</text>
    <text class="lbl" x="82" y="138" text-anchor="end">NEGATIVE</text>
    <text class="lbl" x="558" y="138">POSITIVE</text>
  </g>
  <g class="node">
    <circle cx="496" cy="101" r="3"/><circle cx="393" cy="55" r="3"/>
    <circle cx="247" cy="55" r="3"/><circle cx="144" cy="101" r="3"/>
    <circle cx="144" cy="167" r="3"/><circle cx="247" cy="214" r="3"/>
    <circle cx="393" cy="214" r="3"/><circle cx="496" cy="167" r="3"/>
  </g>
  <circle class="node-open" cx="454" cy="73" r="3.5"/>
  <g font-size="11.5">
    <text x="504" y="105">cheerful</text>
    <text x="401" y="59">excited</text>
    <text x="239" y="59" text-anchor="end">angry</text>
    <text x="136" y="105" text-anchor="end">anxious</text>
    <text x="136" y="171" text-anchor="end">gloomy</text>
    <text x="239" y="218" text-anchor="end">sad</text>
    <text x="401" y="218">serene</text>
    <text x="504" y="171">relaxed</text>
    <text x="462" y="77" font-size="10" class="dim">a new tag</text>
  </g>
</svg>
<figcaption>The two axes turn the mood vocabulary into a space with coordinates, so a new tag has somewhere to land instead of being appended to the end of a list.</figcaption>
</figure>

Anchoring to an existing scheme sounds like a small detail, but it is what determines whether the label set can grow: when a new tag is needed, there is a structure telling you where it belongs, instead of a flat list anyone can append to at will.

On the model side, this layer runs two networks in parallel. One is a multi-label classifier built on a transformer architecture for audio spectrograms, with four separate heads for the first four tag groups. The other is a dedicated language identification network built on an architecture common in speech processing. Splitting the two rather than folding them into one multi-head network was deliberate: language identification keys off phonetic cues while genre classification keys off harmonic and rhythmic ones, and forcing them to share a trunk tends to make the two tasks pull against each other.

### Layer two: representations and indexing

This is the bottleneck of the whole system. Every track becomes four vectors living in four different spaces:

- **An audio vector**, taken from the hidden states of the spectrogram network and averaged over the time axis.
- **A tag vector**, produced by a multilingual text embedding model. The interesting part: rather than encoding the tags as a binary vector, the system **stitches them into a natural Vietnamese sentence** — roughly "Title X. Artist Y. Genre A. Mood B. Instruments C" — and embeds that. A query like "sad songs with guitar" then matches content without any hand-written dictionary mapping keywords to tags.
- **A lyrics vector**, from the same text embedding model, run over the lyrics.
- **A behavior vector**, read off the factor matrices of the collaborative filtering model.

<figure class="diagram">
<svg viewBox="0 0 640 190" role="img" aria-label="Two ways to turn tags into a vector: stitch them into a natural sentence and embed it, versus a binary encoding that yields a sparse vector">
  <defs><marker id="rec-a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="156" y="18">THE PATH TAKEN</text>
    <text class="lbl" x="156" y="116">THE PATH DROPPED</text>
  </g>
  <rect class="box-soft" x="0" y="75" width="132" height="58"/>
  <rect class="box-ok" x="156" y="28" width="168" height="58"/>
  <rect class="box-ok" x="348" y="33" width="128" height="48"/>
  <rect class="box-ok" x="500" y="28" width="136" height="58"/>
  <rect class="box-warn" x="156" y="126" width="168" height="48"/>
  <rect class="box-warn" x="500" y="121" width="136" height="58"/>
  <g class="flow" marker-end="url(#rec-a3)">
    <path d="M132 96 H144 V57 H152"/><path d="M132 112 H144 V150 H152"/>
    <path d="M324 57 H344"/><path d="M476 57 H496"/><path d="M324 150 H496"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="95">Separate tags</text>
    <text x="10" y="109" font-size="10" class="dim">genre, mood,</text>
    <text x="10" y="123" font-size="10" class="dim">instruments, vocals</text>
    <text x="166" y="48">One natural sentence</text>
    <text x="166" y="62" font-size="10" class="dim">Title X. Genre A.</text>
    <text x="166" y="76" font-size="10" class="dim">Mood B. Instruments C.</text>
    <text x="358" y="53">Text embedding</text>
    <text x="358" y="67" font-size="10" class="dim">multilingual</text>
    <text x="510" y="48">Dense vector</text>
    <text x="510" y="62" font-size="10" class="dim">matches free-text</text>
    <text x="510" y="76" font-size="10" class="dim">queries directly</text>
    <text x="166" y="146">Binary encoding</text>
    <text x="166" y="160" font-size="10" class="dim">one dimension per tag</text>
    <text x="510" y="141">Sparse vector</text>
    <text x="510" y="155" font-size="10" class="dim">no match for free</text>
    <text x="510" y="169" font-size="10" class="dim">text queries</text>
    <text x="352" y="143" font-size="10" class="dim">no model in this path</text>
  </g>
</svg>
<figcaption>The sentence is the bridge that brings a user's query and the content description into one space; a binary encoding has no such bridge.</figcaption>
</figure>

Each of the four gets its own index, built with an approximate nearest neighbor library over a hierarchical graph structure. The idea is a stack of graph layers: sparse at the top so a search can take long jumps, dense at the bottom so it can refine — which makes search time grow logarithmically rather than linearly with the number of items.

<figure class="diagram">
<svg viewBox="0 0 640 248" role="img" aria-label="A hierarchical graph: a sparse top layer with long edges, denser layers below, and a search path descending from an entry point to the target">
  <defs><marker id="rec-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-soft" x="126" y="28" width="488" height="48"/>
  <rect class="box-soft" x="126" y="104" width="488" height="50"/>
  <rect class="box-soft" x="126" y="180" width="488" height="50"/>
  <g class="grid dashed">
    <path d="M140 62 V138"/><path d="M288 40 V142"/><path d="M510 58 V116"/>
    <path d="M140 138 V214"/><path d="M214 116 V218"/><path d="M288 142 V216"/>
    <path d="M362 118 V214"/><path d="M436 140 V218"/><path d="M510 116 V212"/>
    <path d="M584 140 V216"/>
  </g>
  <g class="edge">
    <path d="M140 62 L288 40"/><path d="M288 40 L510 58"/><path d="M140 62 L510 58"/>
    <path d="M140 138 L214 116"/><path d="M214 116 L288 142"/><path d="M288 142 L362 118"/>
    <path d="M362 118 L436 140"/><path d="M436 140 L510 116"/><path d="M510 116 L584 140"/>
    <path d="M140 138 L288 142"/><path d="M362 118 L510 116"/>
    <path d="M140 214 L177 192"/><path d="M177 192 L214 218"/><path d="M214 218 L251 194"/>
    <path d="M251 194 L288 216"/><path d="M288 216 L325 190"/><path d="M325 190 L362 214"/>
    <path d="M362 214 L399 196"/><path d="M399 196 L436 218"/><path d="M436 218 L473 192"/>
    <path d="M473 192 L510 212"/><path d="M510 212 L547 196"/><path d="M547 196 L584 216"/>
    <path d="M140 214 L214 218"/><path d="M288 216 L362 214"/><path d="M436 218 L510 212"/>
  </g>
  <g class="node">
    <circle cx="288" cy="40" r="3"/><circle cx="510" cy="58" r="3"/>
    <circle cx="140" cy="138" r="3"/><circle cx="214" cy="116" r="3"/>
    <circle cx="288" cy="142" r="3"/><circle cx="362" cy="118" r="3"/>
    <circle cx="436" cy="140" r="3"/><circle cx="510" cy="116" r="3"/>
    <circle cx="584" cy="140" r="3"/>
    <circle cx="140" cy="214" r="3"/><circle cx="177" cy="192" r="3"/>
    <circle cx="214" cy="218" r="3"/><circle cx="251" cy="194" r="3"/>
    <circle cx="288" cy="216" r="3"/><circle cx="325" cy="190" r="3"/>
    <circle cx="362" cy="214" r="3"/><circle cx="399" cy="196" r="3"/>
    <circle cx="473" cy="192" r="3"/><circle cx="510" cy="212" r="3"/>
    <circle cx="547" cy="196" r="3"/><circle cx="584" cy="216" r="3"/>
  </g>
  <circle class="node-open" cx="140" cy="62" r="4"/>
  <circle class="node-accent" cx="436" cy="218" r="4.5"/>
  <path class="flow" marker-end="url(#rec-a4)" d="M140 62 L288 40 L288 142 L362 118 L362 214 L399 196 L436 218"/>
  <g class="dim">
    <text class="lbl" x="0" y="34" font-size="9.5">TOP LAYER</text>
    <text x="0" y="48" font-size="10">few points, long edges</text>
    <text class="lbl" x="0" y="110" font-size="9.5">MIDDLE LAYER</text>
    <text x="0" y="124" font-size="10">denser, shorter edges</text>
    <text class="lbl" x="0" y="186" font-size="9.5">BOTTOM LAYER</text>
    <text x="0" y="200" font-size="10">densest, shortest edges</text>
    <text x="152" y="84" font-size="10">entry point</text>
    <text x="436" y="236" font-size="10" text-anchor="middle">target</text>
  </g>
</svg>
<figcaption>Every descent narrows the region still to be searched. The number of layers grows with the logarithm of the number of points, and so does the number of steps.</figcaption>
</figure>

### Layer three: hybrid search

A query runs down two branches in parallel. The vector branch embeds the query into the same space as the content and looks for neighbors. The keyword branch does string matching against titles, artist names, and tags. The two branches produce two lists, and a fusion step merges them together with two secondary factors, popularity and recency.

Queries can be text or a clip of audio; the latter goes straight into the audio vector index.

### Layer four: multi-source recommendation

Three candidate sources run independently and are then merged.

**Content-based.** Average the vectors of the tracks a user has liked to get a taste profile, then look for that profile's neighbors. For a new user who has liked nothing yet, the profile is built from the most popular tracks — a cheap and simple cold-start fallback.

**Collaborative filtering.** Alternating least squares over the interaction matrix. The idea is to factor the user-by-item matrix into two smaller factor matrices, then alternately hold one side fixed and solve for the other — each step is a least squares problem with a closed-form solution, so it converges quickly and parallelizes well.

<figure class="diagram">
<svg viewBox="0 0 640 170" role="img" aria-label="A sparse interaction matrix approximated by the product of two narrow factor matrices, solved by alternately holding one side fixed and solving the other">
  <defs><marker id="rec-a5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="20" y="32">INTERACTIONS</text>
    <text class="lbl" x="170" y="32">USER FACTORS</text>
    <text class="lbl" x="228" y="66">ITEM FACTORS</text>
    <text class="lbl" x="440" y="32">ALTERNATING STEP</text>
  </g>
  <rect class="box" x="20" y="42" width="130" height="91"/>
  <g class="grid">
    <path d="M33 42 V133"/><path d="M46 42 V133"/><path d="M59 42 V133"/><path d="M72 42 V133"/>
    <path d="M85 42 V133"/><path d="M98 42 V133"/><path d="M111 42 V133"/><path d="M124 42 V133"/>
    <path d="M137 42 V133"/>
    <path d="M20 55 H150"/><path d="M20 68 H150"/><path d="M20 81 H150"/>
    <path d="M20 94 H150"/><path d="M20 107 H150"/><path d="M20 120 H150"/>
  </g>
  <g class="cell-on">
    <rect x="20" y="42" width="13" height="13"/><rect x="59" y="42" width="13" height="13"/>
    <rect x="111" y="42" width="13" height="13"/><rect x="85" y="55" width="13" height="13"/>
    <rect x="46" y="68" width="13" height="13"/><rect x="124" y="68" width="13" height="13"/>
    <rect x="72" y="81" width="13" height="13"/><rect x="137" y="81" width="13" height="13"/>
    <rect x="98" y="94" width="13" height="13"/><rect x="33" y="107" width="13" height="13"/>
    <rect x="111" y="107" width="13" height="13"/><rect x="46" y="120" width="13" height="13"/>
    <rect x="85" y="120" width="13" height="13"/>
  </g>
  <rect class="box-accent" x="178" y="42" width="26" height="91"/>
  <rect class="box-accent" x="228" y="74" width="130" height="26"/>
  <g class="grid">
    <path d="M191 42 V133"/>
    <path d="M178 55 H204"/><path d="M178 68 H204"/><path d="M178 81 H204"/>
    <path d="M178 94 H204"/><path d="M178 107 H204"/><path d="M178 120 H204"/>
    <path d="M241 74 V100"/><path d="M254 74 V100"/><path d="M267 74 V100"/><path d="M280 74 V100"/>
    <path d="M293 74 V100"/><path d="M306 74 V100"/><path d="M319 74 V100"/><path d="M332 74 V100"/>
    <path d="M345 74 V100"/><path d="M228 87 H358"/>
  </g>
  <g font-size="13" text-anchor="middle">
    <text x="164" y="92">≈</text>
    <text x="216" y="92">×</text>
  </g>
  <path class="flow" marker-end="url(#rec-a5)" d="M374 92 H428"/>
  <rect class="box" x="440" y="44" width="196" height="44"/>
  <rect class="box" x="440" y="110" width="196" height="44"/>
  <g class="flow" marker-end="url(#rec-a5)">
    <path d="M490 88 V104"/><path d="M586 110 V94"/>
  </g>
  <g font-size="11.5">
    <text x="450" y="64">Hold V fixed, solve U</text>
    <text x="450" y="78" font-size="10" class="dim">each step has a closed form</text>
    <text x="450" y="130">Hold U fixed, solve V</text>
    <text x="450" y="144" font-size="10" class="dim">then swap the two roles</text>
  </g>
  <g class="dim" font-size="10">
    <text x="20" y="150">most cells are empty</text>
    <text x="378" y="84">solved by</text>
    <text x="520" y="105" text-anchor="middle">alternate</text>
  </g>
</svg>
<figcaption>The two factor matrices together are far smaller than the original, and they are dense — that is where the empty cells get filled in.</figcaption>
</figure>

**Sequential.** A transformer takes the sequence of items a user has just consumed and predicts the next one, with a causal mask so each position can only look backwards.

All three have the same shape: they return candidates with scores, and a linear fusion function combines them into the final ranking, again with popularity and recency added on top.

### Implicit signals: turning behavior into numbers

One design detail here is worth carrying elsewhere. The raw interaction data is nothing but discrete events — play, like, unlike. Before any of it reaches a model, each event is converted into a real-valued weight by a handful of rules:

- An early skip — barely any of the track played before moving on — carries a **negative** value. It is evidence of dislike, not a neutral event.
- A near-complete listen gets a multiplier: a stronger positive signal than stopping halfway.
- An interaction the user sought out counts for more than one that arrived through a recommendation, because it reflects deliberate intent.
- Recent interactions weigh more than old ones, decaying over time.

<figure class="diagram">
<svg viewBox="0 0 640 256" role="img" aria-label="A continuous weight scale with a negative side: an early skip sits below zero, listening depths above it, plus a curve for decay over time">
  <defs><marker id="rec-a6" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-warn" x="40" y="92" width="130" height="16"/>
  <rect class="box-ok" x="170" y="92" width="434" height="16"/>
  <path class="axis" d="M170 84 V116"/>
  <text class="num" x="170" y="128" text-anchor="middle">0</text>
  <g class="edge">
    <path d="M88 100 V70"/><path d="M224 100 V70"/><path d="M386 100 V70"/>
    <path d="M468 100 V134"/><path d="M560 100 V134"/>
  </g>
  <g class="node">
    <circle cx="88" cy="100" r="3.5"/><circle cx="224" cy="100" r="3.5"/>
    <circle cx="386" cy="100" r="3.5"/><circle cx="468" cy="100" r="3.5"/>
    <circle cx="560" cy="100" r="3.5"/>
  </g>
  <path class="flow" marker-end="url(#rec-a6)" d="M476 120 H552"/>
  <path class="axis" d="M40 190 V232 H248"/>
  <path class="curve" d="M42 194 C 92 216, 152 228, 244 230"/>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="40" y="34">WEIGHT OF ONE EVENT</text>
    <text class="lbl" x="40" y="86">NEGATIVE</text>
    <text class="lbl" x="600" y="86" text-anchor="end">POSITIVE</text>
    <text class="lbl" x="40" y="180">DECAY OVER TIME</text>
  </g>
  <g font-size="11.5" text-anchor="middle">
    <text x="88" y="64">an early skip</text>
    <text x="224" y="64">half a listen</text>
    <text x="386" y="64">a near-full listen</text>
    <text x="468" y="148">recommended</text>
    <text x="560" y="148">sought out</text>
  </g>
  <g class="dim" font-size="10">
    <text x="514" y="114" text-anchor="middle">counts more</text>
    <text x="40" y="246">recent</text>
    <text x="248" y="246" text-anchor="end">long ago</text>
    <text x="264" y="216">the same behavior weighs less the older it is</text>
  </g>
</svg>
<figcaption>A liked-or-not table holds two values. This scale is continuous, has a negative side, and fades as the event recedes into the past.</figcaption>
</figure>

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

<figure class="diagram">
<svg viewBox="0 0 640 260" role="img" aria-label="A four-level funnel narrowing from the whole catalog through candidate generation and scoring to re-ranking, each level optimized for a different goal">
  <defs><marker id="rec-a7" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-soft" x="20" y="30" width="320" height="30"/>
  <rect class="box" x="58" y="76" width="244" height="56"/>
  <rect class="box" x="94" y="148" width="172" height="42"/>
  <rect class="box-accent" x="118" y="206" width="124" height="42"/>
  <g class="flow" marker-end="url(#rec-a7)">
    <path d="M180 60 V72"/><path d="M180 132 V144"/><path d="M180 190 V202"/>
  </g>
  <g font-size="11.5">
    <text x="30" y="50">The whole catalog</text>
    <text x="68" y="96">Candidate generation</text>
    <text x="68" y="110" font-size="10" class="dim">several generators in parallel</text>
    <text x="68" y="124" font-size="10" class="dim">cheap, biased toward recall</text>
    <text x="104" y="168">Scoring</text>
    <text x="104" y="182" font-size="10" class="dim">expensive, feature-rich</text>
    <text x="128" y="226">Re-ranking</text>
    <text x="128" y="240" font-size="10" class="dim">business rules</text>
  </g>
  <g class="dim" font-size="10">
    <text x="192" y="143">down to a small set</text>
    <text x="192" y="201">smaller still</text>
    <text x="256" y="232">the final list</text>
  </g>
  <g class="dim">
    <text class="lbl" x="368" y="98" font-size="9.5">OPTIMIZED FOR RECALL</text>
    <text x="368" y="112" font-size="10">better too many than too few</text>
    <text class="lbl" x="368" y="163" font-size="9.5">OPTIMIZED FOR PRECISION</text>
    <text x="368" y="177" font-size="10">get the order right</text>
    <text class="lbl" x="368" y="221" font-size="9.5">OPTIMIZED FOR EXPERIENCE</text>
    <text x="368" y="235" font-size="10">diversity, seen-filter, exploration</text>
  </g>
</svg>
<figcaption>Each stage trades recall for precision. Staging also lets each part be measured on its own, which is how you find the one that is the bottleneck.</figcaption>
</figure>

The staging is not only about speed. It also lets each part be improved independently, and lets you measure which stage is currently the bottleneck.

**Two model families for two stages.** Matrix factorization is fast and cheap but cannot use anything beyond identifiers. A two-tower network — one tower encoding the user, one encoding the item, both projecting into a shared space — accepts rich features and handles new users better, at a higher cost. The usual pairing is the light model at candidate generation and the heavy one at scoring.

**Offline metrics have to connect to real behavior.** Ranking metrics like nDCG account for position: a correct result at rank one is worth more than the same result at rank ten. Alongside them sit the online metrics — click-through rate, watch time, completion rate. What matters is picking the offline metric that predicts the online one the organization actually cares about.

One variant worth noting is normalized cross-entropy, which divides the model's loss by that of a baseline always predicting the average rate. A value above one means the model is worse than the baseline — the metric announces its own failures instead of leaving the reader to work them out.

**Cross-modal search needs a shared space.** For a text query to reach audio content, the two have to live in the same vector space, and that only happens when a model is trained contrastively on text-audio pairs. Placing two separate encoders side by side and adding their scores does not produce that capability — it only lets you compare text against the textual description of the content, which is exactly how the system above works.

## A few things to take away

**The event-to-signal step matters more than it looks.** The formula that turns interactions into weights — distinguishing a skip from a full listen, a self-directed play from a recommended one, recent from long ago — delivers more value per line of code than anything else in the system.

**Fusing scores from several sources means normalizing first.** Scores from three sources typically live on completely different scales: one is a similarity bounded in the unit interval, one is an unbounded dot product, one is a probability over thousands of classes and therefore always tiny. Adding them with weights as-is means the small-scale source contributes almost nothing, however large its nominal weight. Normalizing onto a common scale, or fusing by rank instead, is not optional.

<figure class="diagram">
<svg viewBox="0 0 640 212" role="img" aria-label="Three score sources on one axis: the probability bar all but vanishes when the scores are added as-is, and comes back into balance after normalization">
  <defs><marker id="rec-a8" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-warn" x="2" y="24" width="302" height="176"/>
  <rect class="box-ok" x="336" y="24" width="302" height="176"/>
  <g class="axis">
    <path d="M12 170 H294"/><path d="M346 170 H628"/>
  </g>
  <g class="bar">
    <rect x="44" y="159" width="40" height="11"/>
    <rect x="124" y="52" width="40" height="118"/>
    <rect x="378" y="76" width="40" height="94"/>
    <rect x="458" y="58" width="40" height="112"/>
  </g>
  <g class="bar-accent">
    <rect x="204" y="168" width="40" height="2"/>
    <rect x="538" y="90" width="40" height="80"/>
  </g>
  <path class="flow" marker-end="url(#rec-a8)" d="M308 112 H332"/>
  <g class="dim">
    <text class="lbl" x="12" y="42" font-size="9.5">ADDED AS-IS</text>
    <text x="12" y="56" font-size="10">three different scales</text>
    <text class="lbl" x="346" y="42" font-size="9.5">NORMALIZED FIRST</text>
    <text x="346" y="56" font-size="10">or fused by rank</text>
    <text x="224" y="158" font-size="10" text-anchor="middle">almost disappears</text>
  </g>
  <g font-size="10" text-anchor="middle">
    <text x="64" y="186">cosine similarity</text>
    <text x="144" y="186">dot product</text>
    <text x="224" y="186">probability</text>
    <text x="398" y="186">cosine similarity</text>
    <text x="478" y="186">dot product</text>
    <text x="558" y="186">probability</text>
  </g>
</svg>
<figcaption>A nominal weight does not decide the real contribution; the scale does. Normalizing is what hands that decision back to the weight.</figcaption>
</figure>

**The distance metric has to match how the vectors were produced.** Nearest neighbor indexes default to Euclidean distance, while most semantic representations are designed to be compared by cosine. Without normalizing vector length before indexing, ranking ends up driven by magnitude rather than direction alone.

**Build the representation layer before anything else.** Of the four layers, the last three all read indexes produced by layer two. Rebuilding a system like this, that ordering is forced — and it is also where investment pays off most, because representation quality sets a ceiling on everything downstream.
