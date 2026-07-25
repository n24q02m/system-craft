---
title: "Five principles that carry across every ML system"
description: "The engineering habits that hold their value in every domain: build checkable invariants, guard against leakage, set a frame of reference, choose the right measure, and keep the configuration with the artifact."
lang: "en"
order: 6
field: "META"
topics: ["ml practice", "data leakage", "baselines", "metric selection", "technical debt"]
---

The five posts before this one covered five different domains: content recommendation, biometrics, language, computer vision, time series. They differ in their data, in their architectures and in how they are measured. But one group of principles turned up in all five, and none of them has anything to do with choosing a model.

This post collects them. What they have in common is that they are all **process habits**, cheap to adopt, and their value grows with the complexity of the system.

## Principle one: build checkable invariants at every layer

<figure class="diagram">
<svg viewBox="0 0 640 178" role="img" aria-label="Comparison of how failures show up in conventional software against machine learning systems">
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">CONVENTIONAL SOFTWARE</text>
    <text class="lbl" x="340" y="14" font-size="9.5">MACHINE LEARNING SYSTEMS</text>
  </g>
  <rect class="box" x="0" y="24" width="300" height="130"/>
  <rect class="box-accent" x="340" y="24" width="300" height="130"/>
  <g font-size="11.5">
    <text x="14" y="48">Failures announce themselves</text>
    <text x="354" y="48">Failures get absorbed</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="14" y="74">the program stops</text>
    <text x="14" y="94">an obviously absurd value</text>
    <text x="14" y="114">a type mismatch</text>
    <text x="354" y="74">a probability always sits in range</text>
    <text x="354" y="94">a list always has the right length</text>
    <text x="354" y="114">a metric still computes</text>
  </g>
  <g font-size="10.5">
    <text x="14" y="140">the signal comes for free</text>
    <text x="354" y="140">you build the invariants yourself</text>
  </g>
</svg>
<figcaption>Machine learning output almost always lands inside the valid range, so nothing naturally signals that something has gone wrong.</figcaption>
</figure>

Machine learning differs from traditional software in one fundamental way. In traditional software, a broken function usually produces observably broken behaviour: the program stops, or it returns a value that is obviously nonsense. In machine learning, the output almost always falls inside the valid range, since a probability is always between 0 and 1 and a recommendation list always has the requested number of items, so nothing naturally signals that something is off.

The way to compensate is to build **invariants** up front, meaning conditions that must always hold if the system is working, and to check them at startup rather than when analysing results. A few that can be applied immediately:

- A vector index has to contain a number of entries matching the number of items being served. If the index covers only a small fraction of the catalogue, the service should refuse to start rather than serve quietly.
- The fraction of items with an empty representation should be tracked as an operational metric, on the same footing as latency.
- Recommender output should be measured for diversity. If most users receive the same list, the system is not personalising, whatever the ranking metric says.
- A model, when loaded, should carry its own metrics along with a reference point; if the metric falls below the reference, loading should fail.

What these checks have in common is that they turn a silent failure into a loud one. That is the entire point, and it is also why they are worth writing before anyone needs them.

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="The path a failure takes through the layers without an invariant and with an invariant checked at startup">
  <defs><marker id="meta-a1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="12" font-size="9.5">WITHOUT AN INVARIANT</text>
  <rect class="box" x="0" y="22" width="100" height="50"/>
  <rect class="box" x="122" y="22" width="100" height="50"/>
  <rect class="box" x="244" y="22" width="100" height="50"/>
  <rect class="box-warn" x="366" y="22" width="274" height="50"/>
  <path class="flow" d="M101,47 L117,47" marker-end="url(#meta-a1)"/>
  <path class="flow" d="M223,47 L239,47" marker-end="url(#meta-a1)"/>
  <path class="flow" d="M345,47 L361,47" marker-end="url(#meta-a1)"/>
  <text class="lbl dim" x="0" y="106" font-size="9.5">WITH A STARTUP INVARIANT</text>
  <rect class="box" x="0" y="116" width="100" height="50"/>
  <rect class="box-ok" x="122" y="116" width="222" height="50"/>
  <rect class="box dim" x="366" y="116" width="274" height="50"/>
  <path class="flow" d="M101,141 L117,141" marker-end="url(#meta-a1)"/>
  <path class="flow dashed" d="M345,141 L363,141"/>
  <g font-size="11.5">
    <text x="12" y="42">data</text>
    <text x="134" y="42">training</text>
    <text x="256" y="42">serving</text>
    <text x="378" y="42">surfaces only at result analysis</text>
    <text x="12" y="136">data</text>
    <text x="134" y="136">the invariant stops it here</text>
    <text class="dim" x="378" y="136">later layers never run</text>
  </g>
  <g font-size="10" class="dim">
    <text x="12" y="58">starts here</text>
    <text x="134" y="58">silent</text>
    <text x="256" y="58">silent</text>
    <text x="12" y="152">starts here</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="378" y="58">or never surfaces at all</text>
    <text x="134" y="152">checked at startup</text>
    <text x="378" y="152">no wrong result to read</text>
  </g>
  <text class="dim" x="0" y="188" font-size="10.5">The invariant runs at startup, not during result analysis.</text>
</svg>
<figcaption>What the invariant changes is where on the timeline the failure is caught: at the layer that produced it, rather than at the end of the pipeline.</figcaption>
</figure>

This is not a new observation. A widely cited work on **technical debt in machine learning systems** describes exactly this phenomenon at industrial scale: ML systems accumulate a particular kind of debt that traditional software engineering tooling cannot see, with eroded boundaries between components, entanglement to the point where changing one feature changes everything, undeclared consumers of data, and hidden feedback loops. The bill for this debt arrives late, and it arrives as maintenance cost rather than as a bug.

## Principle two: ask whether this information exists at prediction time

Data leakage is when information that should not be known at prediction time makes its way into training. The basic form is well known: a random split on data that has a time order. The other forms are considerably subtler.

**Global information leaking into preprocessing.** Normalising with a mean and standard deviation computed over the entire dataset, held-out portion included, is the classic example. So is selecting features by their correlation with the label computed over the entire dataset.

**Object attributes leaking into event timestamps.** If the moment a person interacted with a piece of content is derived from an attribute of that content rather than from real behaviour, then every behaviour sequence gets forced into the same shape, and a model with a time axis will learn that shape instead of learning preferences.

**Units repeated across splits.** Many samples come from the same source, several frames from one video, several passages from one article, several measurements from one station, and if they land in both the training set and the test set then the model has already seen the answer in a slightly different form.

<figure class="diagram">
<svg viewBox="0 0 640 286" role="img" aria-label="Three forms of data leakage: global information into preprocessing, an object attribute into event timestamps, and units repeated across splits">
  <defs><marker id="meta-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="12" font-size="9.5">GLOBAL INFORMATION INTO PREPROCESSING</text>
  <rect class="box-warn" x="0" y="22" width="196" height="44"/>
  <rect class="box" x="8" y="30" width="88" height="28"/>
  <rect class="box" x="100" y="30" width="88" height="28"/>
  <path class="flow" d="M197,44 L214,44" marker-end="url(#meta-a2)"/>
  <rect class="box" x="216" y="30" width="84" height="28"/>
  <rect class="box" x="340" y="30" width="88" height="28"/>
  <path class="flow" d="M429,44 L446,44" marker-end="url(#meta-a2)"/>
  <rect class="box-ok" x="448" y="30" width="88" height="28"/>
  <path class="flow" d="M537,44 L554,44" marker-end="url(#meta-a2)"/>
  <rect class="box" x="556" y="30" width="84" height="28"/>
  <g font-size="10.5">
    <text x="16" y="48">training</text>
    <text x="108" y="48">held-out</text>
    <text x="224" y="48">normalise</text>
    <text x="348" y="48">training</text>
    <text x="456" y="48">normalise</text>
    <text x="564" y="48">held-out</text>
  </g>
  <g font-size="10" class="dim">
    <text x="0" y="82">mean and standard deviation over all the data</text>
    <text x="340" y="82">computed on the training part, then applied</text>
  </g>
  <text class="lbl dim" x="0" y="106" font-size="9.5">OBJECT ATTRIBUTE INTO EVENT TIMESTAMP</text>
  <rect class="box" x="0" y="116" width="150" height="44"/>
  <path class="flow" d="M151,138 L168,138" marker-end="url(#meta-a2)"/>
  <rect class="box-warn" x="170" y="116" width="170" height="44"/>
  <path class="flow" d="M341,138 L358,138" marker-end="url(#meta-a2)"/>
  <g class="edge">
    <line x1="376" y1="124" x2="466" y2="124"/>
    <line x1="376" y1="138" x2="466" y2="138"/>
    <line x1="376" y1="152" x2="466" y2="152"/>
  </g>
  <g class="node">
    <circle cx="376" cy="124" r="3"/>
    <circle cx="406" cy="124" r="3"/>
    <circle cx="436" cy="124" r="3"/>
    <circle cx="466" cy="124" r="3"/>
    <circle cx="376" cy="138" r="3"/>
    <circle cx="406" cy="138" r="3"/>
    <circle cx="436" cy="138" r="3"/>
    <circle cx="466" cy="138" r="3"/>
    <circle cx="376" cy="152" r="3"/>
    <circle cx="406" cy="152" r="3"/>
    <circle cx="436" cy="152" r="3"/>
    <circle cx="466" cy="152" r="3"/>
  </g>
  <g font-size="10.5">
    <text x="12" y="134">an attribute</text>
    <text x="12" y="148">of the object</text>
    <text x="182" y="134">the timestamp</text>
    <text x="182" y="148">of the event</text>
  </g>
  <text class="dim" x="484" y="142" font-size="10">one shape for all</text>
  <text class="dim" x="0" y="176" font-size="10">the timestamp comes from an attribute rather than from real behaviour, so every sequence takes one shape</text>
  <text class="lbl dim" x="0" y="200" font-size="9.5">UNITS REPEATED ACROSS SPLITS</text>
  <rect class="box-warn" x="0" y="210" width="300" height="48"/>
  <rect class="box-ok" x="340" y="210" width="300" height="48"/>
  <line class="edge dashed" x1="150" y1="216" x2="150" y2="252"/>
  <line class="edge dashed" x1="490" y1="216" x2="490" y2="252"/>
  <g class="node-accent">
    <circle cx="30" cy="228" r="4"/>
    <circle cx="60" cy="228" r="4"/>
    <circle cx="90" cy="228" r="4"/>
    <circle cx="120" cy="228" r="4"/>
    <circle cx="180" cy="228" r="4"/>
    <circle cx="210" cy="228" r="4"/>
    <circle cx="370" cy="228" r="4"/>
    <circle cx="400" cy="228" r="4"/>
    <circle cx="430" cy="228" r="4"/>
  </g>
  <g class="node-open">
    <circle cx="520" cy="228" r="4"/>
    <circle cx="550" cy="228" r="4"/>
    <circle cx="580" cy="228" r="4"/>
  </g>
  <g font-size="10" class="dim">
    <text x="30" y="248">training</text>
    <text x="175" y="248">test</text>
    <text x="370" y="248">training</text>
    <text x="515" y="248">test</text>
    <text x="0" y="274">many samples from one source land in both splits</text>
    <text x="340" y="274">split by source: each source sits in one split only</text>
  </g>
</svg>
<figcaption>All three forms answer the same question wrongly: does this information exist at the moment the prediction has to be made.</figcaption>
</figure>

This is not a problem confined to small projects. A survey of scientific work applying machine learning found leakage errors in hundreds of papers across many fields and sorted them into several distinct types. In one case examined closely, once the leakage was fixed the sophisticated machine learning models no longer outperformed a classical linear regression, and the whole conclusion had to be revisited. The authors propose attaching to each publication a model description sheet that records how the data was split and what the preprocessing steps were, so that errors of this kind surface before publication.

The best defence is a single question, asked of every feature: *does this information genuinely exist at the moment the prediction has to be made?* If the answer is not immediately clear, that is where to dig.

## Principle three: set a frame of reference before measuring

A number on its own says nothing. It acquires meaning only when placed next to a reference point.

That sounds obvious, but building a baseline is the step most often skipped, because it is not interesting and it feels like doing work that is certain to be thrown away.

The consequences are concrete. A metric that sounds low may in fact be good if the problem is hard: in search over a catalogue of hundreds of thousands of items, a small number can still be hundreds of times better than random. Conversely, a metric that sounds high may be worse than guessing the majority class. Without a reference both cases get misread, and the next decision, invest further or stop, is made on a false footing.

<figure class="diagram">
<svg viewBox="0 0 640 196" role="img" aria-label="A single measured value read as two opposite conclusions depending on which reference point is placed beside it">
  <text class="lbl dim" x="0" y="12" font-size="9.5">ONE MEASURED VALUE, TWO REFERENCES</text>
  <line class="axis" x1="30" y1="104" x2="620" y2="104"/>
  <line class="edge dashed" x1="120" y1="66" x2="120" y2="104"/>
  <line class="edge dashed" x1="520" y1="66" x2="520" y2="104"/>
  <line class="edge" x1="380" y1="66" x2="380" y2="104"/>
  <circle class="node-open" cx="120" cy="104" r="4"/>
  <circle class="node-open" cx="520" cy="104" r="4"/>
  <circle class="node-accent" cx="380" cy="104" r="5.5"/>
  <path class="flow" d="M120,120 L120,128 M120,124 L380,124 M380,120 L380,128"/>
  <path class="flow" d="M380,120 L380,128 M380,124 L520,124 M520,120 L520,128"/>
  <text x="380" y="50" font-size="11.5" text-anchor="middle">the same measured value</text>
  <g font-size="10.5" class="dim" text-anchor="middle">
    <text x="120" y="44">random baseline</text>
    <text x="120" y="58">on a huge catalogue</text>
    <text x="520" y="44">majority-class</text>
    <text x="520" y="58">baseline</text>
  </g>
  <g font-size="10.5" text-anchor="middle">
    <text x="250" y="144">many times above it</text>
    <text x="450" y="144">below it</text>
  </g>
  <g font-size="10.5" class="dim" text-anchor="middle">
    <text x="250" y="158">reads as: keep going</text>
    <text x="450" y="158">reads as: stop here</text>
  </g>
  <text class="dim" x="30" y="118" font-size="10">low</text>
  <text class="dim" x="620" y="118" font-size="10" text-anchor="end">high</text>
  <text class="dim" x="0" y="182" font-size="10.5">The number does not change. Only the reference changes, and the conclusion flips.</text>
</svg>
<figcaption>Building the reference point is the step most often skipped, and it is the one that decides which way the number gets read.</figcaption>
</figure>

Reasonable baselines vary by domain: popularity-based recommendation for a recommender; the majority class for classification; the last observed value for a time series. What they share is that all of them take a few minutes to build.

The best-known set of industrial practice guidelines puts this very early in its list of rules: keep the first model simple and get the infrastructure right; test the infrastructure separately from the machine learning; choose a simple, observable and attributable metric for the first objective; catch problems before exporting the model. That ordering is not accidental.

## Principle four: choose the measure to fit the data

Every domain has at least one metric that is popular but misleading under conditions that come up all the time.

**Accuracy on skewed data.** When one class dominates, always guessing that class already gives high accuracy. This is why standards for attack detection present the two error types separately rather than merged, and why class-averaged metrics exist alongside micro-averaged ones.

**Aggregate metrics hiding rare classes.** In object detection, the average across all classes can rise while the class with the fewest samples is getting worse. The datasets designed specifically to expose this all report results split by class frequency group.

**Percentage error when values are near zero.** For data whose normal state is a small value, dividing by the actual value produces meaningless numbers. Baseline-scaled measures were proposed precisely to fix this.

**Metrics that are only comparable under identical conditions.** The perplexity of two language models is comparable only when they share a vocabulary, a condition stated clearly in the standard textbook but very easy to overlook when the tokenisation changes between experiments.

<figure class="diagram">
<svg viewBox="0 0 640 222" role="img" aria-label="Four common measures, each paired with the condition that strips it of meaning">
  <text class="lbl dim" x="0" y="12" font-size="9.5">MEASURE — THE CONDITION THAT VOIDS IT</text>
  <rect class="box" x="0" y="22" width="308" height="76"/>
  <rect class="box" x="332" y="22" width="308" height="76"/>
  <rect class="box" x="0" y="114" width="308" height="76"/>
  <rect class="box" x="332" y="114" width="308" height="76"/>
  <rect class="box-warn" x="12" y="56" width="284" height="30"/>
  <rect class="box-warn" x="344" y="56" width="284" height="30"/>
  <rect class="box-warn" x="12" y="148" width="284" height="30"/>
  <rect class="box-warn" x="344" y="148" width="284" height="30"/>
  <g font-size="11.5">
    <text x="12" y="46">accuracy</text>
    <text x="344" y="46">an averaged aggregate</text>
    <text x="12" y="138">percentage error</text>
    <text x="344" y="138">perplexity</text>
  </g>
  <g font-size="10.5">
    <text x="22" y="75">breaks when one class dominates</text>
    <text x="354" y="75">breaks when a rare class is hidden</text>
    <text x="22" y="167">breaks when true values sit near 0</text>
    <text x="354" y="167">breaks when the vocabularies differ</text>
  </g>
  <text class="dim" x="0" y="212" font-size="10.5">The conditions of applicability are usually not written next to the number.</text>
</svg>
<figcaption>Each of these four measures is correct under its own conditions; the problem is that the conditions do not travel with the number when it is reported.</figcaption>
</figure>

The common pattern: **every metric has conditions of applicability, and those conditions are usually not written next to the number.** When two metrics measuring the same model lead to opposite conclusions, that gap is information to investigate, not an invitation to pick whichever side sounds better.

## Principle five: the artifact must carry the configuration that produced it

Almost all research code has parameters that control the scale of a run: what fraction of the data to use, how many epochs to run, how long to allow. They exist for good reason, because while debugging a pipeline, running on a small slice saves an enormous amount of time.

The risk is that these parameters usually default to values meant for a trial run, and when the time comes for a real run it is easy to forget to reset them. The system still runs, still produces numbers, still saves a model, and nothing signals that anything is wrong.

More dangerous still: when these parameters differ between experiments, every comparison between them is void. If one run used less data than the last, a worse result says nothing about the architecture. The same applies when training stops because a time budget ran out rather than because it converged. The number you get is "the best within a budget", not the result of the method.

The defence is almost trivially simple, and effective: print the effective configuration at the start of every run, and **write it into the same place as the saved model**. A weights file without the configuration that produced it, meaning class count, input size, normalisation, data volume and epoch count, is an uninterpretable binary a few months later.

<figure class="diagram">
<svg viewBox="0 0 640 232" role="img" aria-label="A bare weights file against the same file packaged with the configuration that produced it, and what follows when scale parameters differ between two runs">
  <text class="lbl dim" x="0" y="12" font-size="9.5">WEIGHTS ONLY</text>
  <text class="lbl dim" x="340" y="12" font-size="9.5">WEIGHTS WITH CONFIGURATION</text>
  <rect class="box-warn" x="0" y="22" width="300" height="118"/>
  <rect class="box-ok" x="340" y="22" width="300" height="118"/>
  <g font-size="11.5">
    <text x="12" y="44">a weights file</text>
    <text x="352" y="44">the weights and their configuration</text>
  </g>
  <g font-size="10" class="dim">
    <text x="12" y="66">how many classes?</text>
    <text x="12" y="80">class names in what order?</text>
    <text x="12" y="94">what input size?</text>
    <text x="12" y="108">normalised how?</text>
    <text x="12" y="122">how much data, how many epochs?</text>
    <text x="352" y="66">class count and class order</text>
    <text x="352" y="80">the input size</text>
    <text x="352" y="94">the normalisation</text>
    <text x="352" y="108">data volume and epoch count</text>
    <text x="352" y="122">printed at run time, saved alongside</text>
  </g>
  <rect class="box-soft" x="0" y="164" width="640" height="56"/>
  <rect class="box" x="12" y="174" width="130" height="36"/>
  <rect class="box" x="172" y="174" width="130" height="36"/>
  <path class="flow" d="M151,186 L163,198 M163,186 L151,198"/>
  <g font-size="10.5">
    <text x="22" y="196">run A</text>
    <text x="182" y="196">run B</text>
  </g>
  <text x="318" y="190" font-size="11.5">different scale parameters</text>
  <text class="dim" x="318" y="206" font-size="10">every comparison between the two is void</text>
</svg>
<figcaption>Keeping the configuration with the artifact is what makes two runs comparable at all.</figcaption>
</figure>

## The thread running through it

The five principles look unrelated, but they share a root: **in machine learning, the gap between "it runs" and "it is correct" is much wider than in ordinary software, and nothing naturally closes it.**

Ordinary software tends to expose its own failures. A machine learning system tends to absorb them and carry on producing something that looks like a result. That is why most of the real engineering work is not in choosing a model but in building enough observation points to know what the model is actually doing.

There is one observation from field research worth mentioning here: when practitioners working on high-stakes machine learning problems were interviewed, most reported having run into cascades of compounding failures rooted in data quality. That study's conclusion is right there in its title, which is that everybody wants to do the model work and nobody wants to do the data work.

If only one habit survives from all of the above: before training anything, spend a session proving that the signal you need to learn actually exists in the data, through simple statistics, through looking at a few dozen samples by hand, through a stupid baseline. That session is far cheaper than what it avoids.
