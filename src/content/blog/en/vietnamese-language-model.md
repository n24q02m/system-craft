---
title: "A Vietnamese language model: predicting the next word"
description: "Three tokenization paths for Vietnamese, five architectures built from scratch, and the condition under which two perplexity numbers can be compared at all."
lang: "en"
order: 3
field: "LM"
topics: ["language models", "tokenizer", "perplexity", "LoRA", "vietnamese"]
---

Next-word prediction is the task underneath every language model: given a sequence of words, guess the one that follows. It is simple enough to state in a sentence, yet it contains nearly every interesting problem in language processing — and for Vietnamese it adds one of its own at the very first step.

## Vietnamese and the question of what a word is

In English, whitespace nearly always coincides with a word boundary. In Vietnamese it does not. *Học sinh* ("pupil") is a single word with a meaning of its own, but it is written as two syllables separated by a space. Splitting on whitespace yields two units that mean something quite different on their own.

This is not a purely linguistic curiosity. It determines the model's input, the size of its output space, and the difficulty of the task itself — which makes it the first architectural decision you have to make.

## The system as built

<figure class="diagram">
<svg viewBox="0 0 640 226" role="img" aria-label="Three ways of tokenizing Vietnamese produce three different input sequences">
  <g class="dim"><text class="lbl" x="0" y="14" font-size="9.5">ONE SOURCE SENTENCE</text></g>
  <rect class="box" x="0" y="24" width="640" height="32"/>
  <text x="12" y="45" font-size="12.5">học sinh trường này rất giỏi</text>
  <g class="flow"><path d="M104 56 V80"/><path d="M320 56 V80"/><path d="M536 56 V80"/></g>
  <g class="dim"><text class="lbl" x="0" y="96" font-size="9.5">THREE TOKENIZATIONS</text></g>
  <rect class="box" x="0" y="104" width="200" height="94"/>
  <rect class="box" x="220" y="104" width="200" height="94"/>
  <rect class="box-accent" x="440" y="104" width="200" height="94"/>
  <g font-size="11.5">
    <text x="12" y="126">Whitespace split</text>
    <text x="232" y="126">Vietnamese segmenter</text>
    <text x="452" y="126">Subword units</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="12" y="148">học | sinh | trường | …</text>
    <text x="12" y="167">vocab: frequency-filtered</text>
    <text x="12" y="186">more units, easier per unit</text>
    <text x="232" y="148">học_sinh | trường | …</text>
    <text x="232" y="167">vocab: much larger</text>
    <text x="232" y="186">fewer units, harder per unit</text>
    <text x="452" y="148">học | sinh | trườ | ng | …</text>
    <text x="452" y="167">vocab: fixed, known ahead</text>
    <text x="452" y="186">handles unseen words</text>
  </g>
  <text x="0" y="219" font-size="10.5" class="dim">Because perplexity is normalized per unit, these three branches cannot be compared directly.</text>
</svg>
<figcaption>The same sentence split three ways gives three different unit counts, so the denominator used in the normalization differs too.</figcaption>
</figure>

### Three tokenization paths, three data pipelines

The corpus is a large collection of Vietnamese news articles, each flattened into a single document by concatenating title, summary, and body. Three different pipelines were built over that same corpus.

**Path one — split on whitespace.** The simplest option, with no external dependency. The vocabulary is built by counting frequencies and then **dropping every word below a threshold**, collapsing those into a single unknown-word symbol. Training sequences come from a sliding window over an article's full token stream, so one long article yields a great many samples.

**Path two — segment with a Vietnamese-specific tool.** An existing word segmenter produces units that are real words in the linguistic sense. The vocabulary grows considerably compared to path one, because there are far more syllable combinations forming words than there are individual syllables.

**Path three — split into subword units.** This uses the tokenizer of a pretrained Vietnamese language model, of the byte-pair encoding kind. The vocabulary size is fixed and known in advance, and unseen words are handled by assembling smaller pieces instead of being funneled into one catch-all symbol.

These three are not three configuration variants of the same thing. They produce three different input sequences, three different output-space sizes, and three different difficulty levels for what is nominally the same task.

### Five architectures built from scratch

On each pipeline, five architectures were implemented and trained with the same hyperparameters:

- **RNN** — a plain recurrent network, no gates.
- **GRU** — adds an update gate and a reset gate to control the flow of information.
- **LSTM** — adds a memory cell along with input, forget, and output gates.
- **LSTM with attention** — adds a multi-head attention block over the LSTM's full output sequence before the final state is taken.
- **Transformer** — sinusoidal positional encoding, with blocks of causally masked self-attention, a feed-forward network, layer normalization, and residual connections.

Shared configuration: an embedding layer, two layers, dropout, a fixed maximum sequence length. Optimization with Adam, a scheduler that drops the learning rate on plateau, gradient norm clipping, early stopping, and mixed precision training.

One aspect of the problem framing is worth flagging: these networks take the **hidden state at the last position** of the sequence and project it into vocabulary space — that is, the task is posed as classifying a single word, not as sequence generation. Each training sample therefore yields exactly one learning signal.

### Fine-tuning a pretrained model

Running alongside is a different approach: take pretrained multilingual language models in the few-hundred-million parameter range and fine-tune them on the same task.

The technique is **LoRA**, low-rank adaptation. Rather than updating the full weight matrices, LoRA freezes the original weights and learns an additional pair of low-rank matrices that get added to them. The number of parameters being updated drops sharply, which makes fine-tuning feasible on modest hardware. The target matrices differ by architecture: for one family, the query, key, value, and output projections; for another, the fused block holding all three projections, plus the feed-forward layers.

The important difference in framing: this branch trains as a **standard causal language model** — predicting at every position in the sequence, with padding masked out of the loss. Each sample yields hundreds of learning signals instead of one.

## Background

### Perplexity, and what it takes to compare it

The most common metric for a language model is **perplexity**. The intuition: it measures how surprised the model is, on average, by the test text, and can be read as the effective number of choices it is still hesitating between at each step. A perplexity of one hundred means the model is as uncertain as if it were choosing uniformly among a hundred options.

Formally it is the inverse of the probability the model assigns to the test set, **normalized by the number of units** in the sequence.

That normalization is precisely what leads to a critical condition, stated plainly in the field's standard textbook:

> Note that in computing perplexities, the language model must be constructed without any knowledge
> of the test set, or else the perplexity will be artificially low. **And the perplexity of two
> language models is only comparable if they use identical vocabularies.**

The reason is direct: if one model splits a sentence into twenty units and another splits the same sentence into thirty-five, the denominators already differ. So does the difficulty of each individual prediction — guessing a syllable fragment is far easier than guessing a whole meaningful word.

The practical consequence: **a series of experiments in which each round changes the tokenizer is not a series of comparable improvements.** To find out which tokenization is better, you have to hold everything else fixed and measure with something that does not depend on the unit of division — accuracy on a specific downstream task, for instance.

### Vocabulary size and the long tail

The vocabulary is not merely a configuration number. The model's output layer has to spread probability across the entire vocabulary, so its size drives most of the parameter count and most of the compute cost.

This is why a **rare-word cutoff** exists. Dropping words that appear too few times is not about saving memory; the deeper reason is that a word appearing a handful of times in the whole corpus gives the model no signal to learn a representation from. Keeping it only adds a row to the output matrix that gradients almost never touch.

There is a diagnostic for a vocabulary that has grown too large: ask the model to continue an ordinary opening sentence, and the words it proposes are odd fragments or rare proper nouns rather than common words. That is the sign the output distribution has been taken over by the long tail.

### Why a pretrained model has such a large advantage

A model built from scratch has to learn two things at once: the statistical structure of the language, and the specific task being trained. A pretrained model already has the first and only needs to adapt to the second.

At moderate corpus scale that gap is enormous. It leads to a useful distinction: building an architecture from scratch is an exercise in understanding the principles, while fine-tuning an existing model is the road to a system that works. Both have value, but confusing them means pouring training time into an architecture that has no chance of winning.

## How the industry does this

**Evaluation has to be broader than one number.** Modern evaluation frameworks measure several dimensions at once — not just accuracy but probability calibration, robustness to input noise, fairness, bias, toxicity, and compute cost — across a wide set of scenarios, under identical conditions for every model. The reason is that a model can be strong on one dimension and weak on another, and a single aggregate number hides that. Before these frameworks existed, models were typically measured on a small slice of the scenarios worth caring about.

**Multi-task benchmarks.** The tradition in language understanding evaluation is a suite of different tasks — inference, sentence similarity, classification — rather than a single one, paired with a diagnostic set for analyzing which linguistic phenomena a model handles well or badly. Once models had saturated the first suite, a harder one was built on top of it.

**The Vietnamese ecosystem is now reasonably complete.** There is a publicly released large monolingual language model that outperforms multilingual models on Vietnamese tasks such as part-of-speech tagging, dependency parsing, named entity recognition, and inference. There is a basic toolkit covering word segmentation, POS tagging, and entity recognition. And more recently there is a language understanding benchmark specific to Vietnamese, with more than a dozen tasks assembled by translating existing benchmarks, generating new corpora, and gathering scattered datasets.

This matters because it changes what a sensible starting point looks like: beginning from an existing Vietnamese model is far cheaper than beginning from a randomly initialized embedding layer.

## A few things to take away

**A comparison only means something when everything else is held constant.** Changing the tokenizer changes the unit of measurement; changing the amount of data changes the difficulty. Change both at once and the results cannot be interpreted, even if every run completes successfully.

**Before comparing two perplexity numbers, check that the two models share a vocabulary.** If they do not, the numbers are not comparable, however comparable they may look.

**When two metrics on the same model tell two different stories, the discrepancy is information.** Accuracy only counts whether the right answer appears among the top predictions, so it is fairly coarse. Perplexity averages an exponential, so a handful of samples assigned very low probability is enough to drag it upward. A divergence between the two usually means the evaluation set is too small, or the model is memorizing rather than generalizing.

**The framing of the task determines how efficiently data is used.** On the same corpus, posing it as "predict one word at the end of the sequence" yields far less learning signal than posing it as "predict at every position". This is a choice worth making early, because it governs the whole training budget that follows.
