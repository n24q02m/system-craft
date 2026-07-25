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

This is not a new observation. A widely cited work on **technical debt in machine learning systems** describes exactly this phenomenon at industrial scale: ML systems accumulate a particular kind of debt that traditional software engineering tooling cannot see, with eroded boundaries between components, entanglement to the point where changing one feature changes everything, undeclared consumers of data, and hidden feedback loops. The bill for this debt arrives late, and it arrives as maintenance cost rather than as a bug.

## Principle two: ask whether this information exists at prediction time

Data leakage is when information that should not be known at prediction time makes its way into training. The basic form is well known: a random split on data that has a time order. The other forms are considerably subtler.

**Global information leaking into preprocessing.** Normalising with a mean and standard deviation computed over the entire dataset, held-out portion included, is the classic example. So is selecting features by their correlation with the label computed over the entire dataset.

**Object attributes leaking into event timestamps.** If the moment a person interacted with a piece of content is derived from an attribute of that content rather than from real behaviour, then every behaviour sequence gets forced into the same shape, and a model with a time axis will learn that shape instead of learning preferences.

**Units repeated across splits.** Many samples come from the same source, several frames from one video, several passages from one article, several measurements from one station, and if they land in both the training set and the test set then the model has already seen the answer in a slightly different form.

This is not a problem confined to small projects. A survey of scientific work applying machine learning found leakage errors in hundreds of papers across many fields and sorted them into several distinct types. In one case examined closely, once the leakage was fixed the sophisticated machine learning models no longer outperformed a classical linear regression, and the whole conclusion had to be revisited. The authors propose attaching to each publication a model description sheet that records how the data was split and what the preprocessing steps were, so that errors of this kind surface before publication.

The best defence is a single question, asked of every feature: *does this information genuinely exist at the moment the prediction has to be made?* If the answer is not immediately clear, that is where to dig.

## Principle three: set a frame of reference before measuring

A number on its own says nothing. It acquires meaning only when placed next to a reference point.

That sounds obvious, but building a baseline is the step most often skipped, because it is not interesting and it feels like doing work that is certain to be thrown away.

The consequences are concrete. A metric that sounds low may in fact be good if the problem is hard: in search over a catalogue of hundreds of thousands of items, a small number can still be hundreds of times better than random. Conversely, a metric that sounds high may be worse than guessing the majority class. Without a reference both cases get misread, and the next decision, invest further or stop, is made on a false footing.

Reasonable baselines vary by domain: popularity-based recommendation for a recommender; the majority class for classification; the last observed value for a time series. What they share is that all of them take a few minutes to build.

The best-known set of industrial practice guidelines puts this very early in its list of rules: keep the first model simple and get the infrastructure right; test the infrastructure separately from the machine learning; choose a simple, observable and attributable metric for the first objective; catch problems before exporting the model. That ordering is not accidental.

## Principle four: choose the measure to fit the data

Every domain has at least one metric that is popular but misleading under conditions that come up all the time.

**Accuracy on skewed data.** When one class dominates, always guessing that class already gives high accuracy. This is why standards for attack detection present the two error types separately rather than merged, and why class-averaged metrics exist alongside micro-averaged ones.

**Aggregate metrics hiding rare classes.** In object detection, the average across all classes can rise while the class with the fewest samples is getting worse. The datasets designed specifically to expose this all report results split by class frequency group.

**Percentage error when values are near zero.** For data whose normal state is a small value, dividing by the actual value produces meaningless numbers. Baseline-scaled measures were proposed precisely to fix this.

**Metrics that are only comparable under identical conditions.** The perplexity of two language models is comparable only when they share a vocabulary, a condition stated clearly in the standard textbook but very easy to overlook when the tokenisation changes between experiments.

The common pattern: **every metric has conditions of applicability, and those conditions are usually not written next to the number.** When two metrics measuring the same model lead to opposite conclusions, that gap is information to investigate, not an invitation to pick whichever side sounds better.

## Principle five: the artifact must carry the configuration that produced it

Almost all research code has parameters that control the scale of a run: what fraction of the data to use, how many epochs to run, how long to allow. They exist for good reason, because while debugging a pipeline, running on a small slice saves an enormous amount of time.

The risk is that these parameters usually default to values meant for a trial run, and when the time comes for a real run it is easy to forget to reset them. The system still runs, still produces numbers, still saves a model, and nothing signals that anything is wrong.

More dangerous still: when these parameters differ between experiments, every comparison between them is void. If one run used less data than the last, a worse result says nothing about the architecture. The same applies when training stops because a time budget ran out rather than because it converged. The number you get is "the best within a budget", not the result of the method.

The defence is almost trivially simple, and effective: print the effective configuration at the start of every run, and **write it into the same place as the saved model**. A weights file without the configuration that produced it, meaning class count, input size, normalisation, data volume and epoch count, is an uninterpretable binary a few months later.

## The thread running through it

The five principles look unrelated, but they share a root: **in machine learning, the gap between "it runs" and "it is correct" is much wider than in ordinary software, and nothing naturally closes it.**

Ordinary software tends to expose its own failures. A machine learning system tends to absorb them and carry on producing something that looks like a result. That is why most of the real engineering work is not in choosing a model but in building enough observation points to know what the model is actually doing.

There is one observation from field research worth mentioning here: when practitioners working on high-stakes machine learning problems were interviewed, most reported having run into cascades of compounding failures rooted in data quality. That study's conclusion is right there in its title, which is that everybody wants to do the model work and nobody wants to do the data work.

If only one habit survives from all of the above: before training anything, spend a session proving that the signal you need to learn actually exists in the data, through simple statistics, through looking at a few dozen samples by hand, through a stupid baseline. That session is far cheaper than what it avoids.
