---
title: "Face anti-spoofing: telling a real face from a replay"
description: "Four architectural approaches to presentation attack detection, a mechanism for separating style from content, and how the field standardized measurement."
lang: "en"
order: 2
field: "PAD"
topics: ["anti-spoofing", "domain generalization", "threshold calibration", "ISO/IEC 30107-3", "biometrics"]
---

A face recognition system answers the question of who this person is. It does not answer the question that comes before it: whether the thing in front of the lens is a real human being at all. Hold up a printed photo, a phone playing a pre-recorded video, or a mask, and the recognition stage behind it carries on working normally — it was never designed to be suspicious. The field that fills that gap has a standard name in the international literature: *presentation attack detection*, or PAD.

From a distance this is binary classification: feed in an image, answer live or spoof. But it differs from ordinary binary classification in one decisive way — there is a person on the other side, and that person is actively trying to get through. Nothing obliges an attacker to use an attack type that appears in the training set, that particular printer, that particular screen. Nothing guarantees the camera at the deployment site resembles the one the data was captured with.

This post describes a system built for that problem: the architectures tried in parallel, the mechanism designed specifically to keep the model from latching onto a particular device, and how the field has standardized measurement.

## The system as built

Every approach takes the same input: a face crop produced by a face detector and resized to a fixed resolution. Every approach produces the same output: a binary decision, live or spoof. Since it was not obvious in advance which architecture family suited the problem, the system was built as four approaches running in parallel, sharing one data pipeline and one evaluation protocol so their results stay comparable.

### Approach one: a convolutional network with attention

The backbone is a convolutional network pretrained on a large image dataset, used in both a heavy variant for the unconstrained case and a light variant aimed at mobile devices.

The addition is a CBAM attention block inserted after each block group of the backbone. CBAM has two parts in sequence. Channel attention pools the feature map along the spatial axes using both average and max, passes the two resulting vectors through a shared MLP, sums them, and applies a sigmoid to get a weight per channel. Spatial attention pools along the channel axis, runs the result through a 7x7 convolution and a sigmoid to get a weight per location. The point is to let the network learn which channels and which regions deserve attention, instead of treating the whole feature map uniformly.

The classification head after the backbone is global average pooling, dropout, an intermediate linear layer, batch normalization, ReLU, and a final linear layer returning a single logit.

### Approach two: Vision Transformer

This one swaps the convolutional backbone for a pretrained Vision Transformer, in both a full-size and a very small variant. The image is split into patches, and the representation used for classification comes from the CLS token, feeding a head similar to the one above.

It also has a mode that freezes the entire backbone and trains only the head. That is cheap and reasonable when data is scarce, but it comes with a tradeoff discussed in the background section below.

### Approach three: a GAN with an auxiliary classification branch

This approach uses a generative adversarial network. The generator follows the DCGAN pattern: a latent vector goes through a stack of upsampling and convolution layers to build an image. The discriminator has four stride-2 convolutional blocks with CBAM inserted, then splits into two branches — one judging whether an image is real or generated, which serves the adversarial objective, and an auxiliary one classifying live versus spoof.

The detail worth noting is that the auxiliary branch is the classifier that actually gets used. The adversarial part is a supplementary training signal, there to force the discriminator to learn an informative representation of face images; the generated images themselves are not the goal. That part is trained as a Wasserstein GAN with gradient penalty, a variant chosen for being more stable than the original adversarial formulation.

### Approach four: separating style from content

The three approaches above all start from an off-the-shelf architecture. The fourth goes the other way: a network implemented from scratch and designed specifically for domain generalization, meaning the ability to work on a data source it has never seen.

The underlying idea is to split an image into two components. "Content" is what says whether this is a real person or a copy. "Style" is what reflects which camera, which lighting, which post-processing. The goal is to force the content representation to be independent of the style.

The structure has the following parts:

- A hand-designed multi-stage feature extractor, with no pretrained backbone.
- A content branch and a style branch. The style branch goes through instance normalization and a few fully-connected layers to produce two parameters: a scale and a shift.
- A recombination step using AdaIN, adaptive instance normalization: normalize the content features to zero mean and unit variance, then apply the two style parameters.

The core mechanism is how the training pairs are generated. Within each batch the sample order is shuffled, so the style of one image gets grafted onto the content of another. That hybrid pair is labeled positive if the two source images share a live/spoof class and negative if they do not. A contrastive loss over these pairs pushes the network to place same-class images close together regardless of which device they came from — exactly what is needed when deploying onto unfamiliar hardware.

Two more details. The output is not a single logit but a depth map built through upsampling layers: a real face has three-dimensional structure, while a printed photo or a replayed screen is essentially flat, so depth is a richer supervision signal than a binary label. And there is a domain discriminator branch attached through a gradient reversal layer: that branch tries to guess which data source a sample came from, and the reversal pushes the feature extractor in the opposite direction, toward a representation from which the source cannot be guessed.

The total loss is a weighted sum of three terms: classification, style contrast, and domain adversarial.

### Data and class imbalance

Training runs over several datasets: one collected in-house, plus public benchmarks — a large-scale set that includes video replay attacks, one focused on printed photos, and a video set from a competition in the field. An additional set containing only genuine faces is mixed in to offset the fact that attack samples usually outnumber genuine ones, since producing another attack sample is far cheaper than collecting another real face.

The remaining imbalance is handled inside the binary loss with a positive-class weight, computed from the actual class ratio of the training set rather than hard-coded.

### The evaluation protocol

Four evaluation scenarios are defined, in increasing order of difficulty:

1. Train and test within a single dataset.
2. Train on a mixture of datasets and test on a held-out part of that same mixture.
3. Train on several datasets and test on an entirely different one.
4. The domain generalization scenario: train on multiple sources, test on a source never seen.

Keeping the four separate rather than reporting one number makes the gap between them visible, and it is that gap, not any single figure, that says whether the thing will hold up in the field.

## Background

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="The gap between the training distribution and the deployment distribution">
  <defs><marker id="pad-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">SOURCE DOMAIN — AT TRAINING TIME</text>
    <text class="lbl" x="368" y="14" font-size="9.5">TARGET DOMAIN — AT DEPLOYMENT</text>
  </g>
  <rect class="box" x="0" y="26" width="266" height="132"/>
  <rect class="box-accent" x="368" y="26" width="272" height="132"/>
  <g font-size="11">
    <text x="12" y="50">Specific printers and screens</text>
    <text x="12" y="72">Lab lighting conditions</text>
    <text x="12" y="94">Known cameras</text>
    <text x="12" y="116">Attack types already seen</text>
    <text x="380" y="50">Devices never encountered</text>
    <text x="380" y="72">Arbitrary lighting</text>
    <text x="380" y="94">A completely different camera</text>
    <text x="380" y="116">New attack types</text>
  </g>
  <g class="flow" marker-end="url(#pad-a)"><path d="M266 92 H360"/></g>
  <text class="lbl dim" x="274" y="84" font-size="9">DOMAIN SHIFT</text>
  <g font-size="10.5" class="dim">
    <text x="12" y="146">In-domain scores look optimistic</text>
    <text x="380" y="146">Cross-domain scores are the real test</text>
  </g>
  <text x="0" y="184" font-size="10.5" class="dim">Nothing constrains an attacker to the attack types that appear in the training set.</text>
</svg>
<figcaption>There is always a gap between the two domains. A number measured inside a single dataset says very little about whether the system works in the field.</figcaption>
</figure>

### Why this is not an ordinary binary classification problem

An ordinary classification problem rests on the assumption that training and test data come from the same distribution. For anti-spoofing that assumption is wrong by design. The camera at the deployment site is not the camera the data was shot with, the lighting is not studio lighting, and the attack type may be entirely new. The real difficulty lies in the gap between those two distributions, not in separating genuine from fake on data already seen.

There is also an asymmetry. The "live" class varies in people and capture conditions but remains a closed concept: it is always a real human face in front of a lens. The "spoof" class is open — it covers every known way of faking and every way nobody has thought of yet. Training a binary classifier on a finite set of attack types amounts to teaching it to recognize a few points in a space with no boundary. That is why numbers measured on a held-out split of the same dataset say almost nothing about deployability: the model may well have learned the signature of that particular printer, or the compression artifacts of that particular screen used to create the data.

### Domain shift and domain generalization

The phenomenon where the runtime distribution differs from the training distribution is called domain shift. In this problem a "domain" usually corresponds to a combination of capture device, lighting conditions, and attack-production process — in practice each public dataset is its own domain, since it was collected with one equipment setup and one fixed scenario.

Two responses exist, differing in what they assume. Domain adaptation assumes some data from the target domain is available, even unlabeled, for tuning before deployment. Domain generalization assumes nothing: the model has to work on a domain it has never seen, with no chance to get acquainted first. The way to get there is to train on several source domains at once while forcing the representation to carry no trace of any one of them — if the network cannot tell where the data came from, it has to rely on features common to every domain. The fourth approach above is a direct implementation of that idea, with the style-shuffling mechanism and the gradient reversal branch playing exactly that role.

### The signal lives in high-frequency surface texture

What separates a real face from a photograph of one is usually not shape but surface texture: the moiré banding produced when a camera shoots a pixel display, the paper grain of a print, the unnatural way light reflects off a flat surface. These are all high-frequency signals.

That leads to a practical consideration. Foundation models trained for object classification are optimized to recognize "a cat" whether the image is sharp or blurry, so they tend to discard exactly that class of high-frequency signal as noise. Freezing such a backbone entirely means locking the model into a feature space that has already thrown away the thing you need. Freezing is still a reasonable choice when data is very scarce, but it should be a considered decision rather than a default.

### Two kinds of error with different consequences

The system can be wrong in two ways: it can let an attack through, or it can reject a genuine user. The first is a security problem, the second an experience problem. They do not convert into each other, and the right tradeoff depends on what is being protected: unlocking a news reader and authorizing a bank transfer call for very different operating points on the same curve.

This has direct consequences for how the system is built and how results are published. The model emits a continuous score; the final decision comes from comparing that score against a threshold. Model quality lives in the ranking — how much higher genuine samples score than fakes — while the threshold is an operational parameter chosen afterwards. Collapsing the two into one number destroys information: it cannot tell you whether a poor result comes from a model that discriminates badly or from a cut placed in the wrong spot. So the two should be reported separately, and the threshold should be configurable in the shipped product rather than a constant baked into the code.

## How the industry does this

This field has its own international standard for measurement: **ISO/IEC 30107-3**, full title *Information technology — Biometric presentation attack detection — Part 3: Testing and reporting*, maintained by ISO/IEC JTC 1/SC 37, with the current edition published in 2023 superseding the 2017 one. The standard specifies how to evaluate and how to report, not which algorithm to use.

The metrics it standardizes are three. **APCER** is the proportion of attacks misclassified as genuine. **BPCER** is the proportion of genuine users wrongly rejected — note that the 2017 edition called this quantity NPCER, so older papers need cross-checking. **ACER** is the mean of the two. That the standard keeps the two error types apart instead of folding them into a single accuracy figure is itself an acknowledgment that their consequences differ.

On protocols, the **OULU-NPU** dataset offers a design worth copying. It is video shot on the front cameras of several smartphone models, across multiple environments, with print and video replay attacks. It defines four protocols, and the key point is that each one deliberately places at least one condition in the test set that did not appear during training: a new device, a new environment, or a new attack type. That structure forces the model to generalize rather than memorize.

Other benchmarks share the spirit. **SiW** (Liu, Jourabloo, Liu, CVPR 2018) introduced auxiliary supervision: rather than a binary label alone, the model also learns a depth map and an rPPG signal — the pulse trace visible in very small changes of skin color, which a printed photo does not have; the paper reports both intra-dataset and cross-dataset results. **CASIA-SURF** (CVPR 2019) is a large-scale multimodal benchmark with three modalities, RGB, depth, and IR, shipped with a standard protocol.

For presenting results, the **DET curve** (Martin et al., Eurospeech 1997, *The DET curve in assessment of detection task performance*) was proposed for exactly this class of problem with two competing error types. It plots on log axes, which stretches out the region around the equal-error point — the region that actually matters when picking an operating threshold — and makes comparison easier than a standard ROC does.

International PAD competitions rank entries by ACER and fix the decision threshold at the EER on a validation set instead of picking an arbitrary number. That small detail carries a lot: it turns threshold selection into a reproducible procedure rather than a choice that could, deliberately or not, flatter the results.

Two reporting principles follow. First, a number at a fixed threshold is only one point on a curve, so the full ROC or DET curve and the EER should be published alongside it to give the reader the whole picture. Second, when the test set is class-imbalanced — and in this field it almost always is, since attack samples are easier to produce than genuine ones — a single pooled accuracy figure reflects the class ratio more than it reflects model quality.

## A few things to take away

**Prefer threshold-independent metrics when evaluating a model.** Area under the ROC curve, or EER, speaks to the model's ranking ability; accuracy at one threshold speaks to the quality of one operational decision. The two are separate concerns, and conflating them produces wrong conclusions about both.

**Design the evaluation protocol so it can fail.** The way OULU-NPU places unseen conditions in the test set is a pattern worth copying for any problem with domain shift. A protocol that never reports a failure carries no information.

**Build invariance into the architecture instead of hoping data teaches it.** In-batch style shuffling and the gradient reversal branch are two ways of telling the network that device and lighting are not what it should be learning. When you know in advance which direction of variation is noise, encoding that into the loss beats collecting more data.

**Choose the operating point by the consequence of each error type.** Because the two errors cost different amounts in different applications, the shipped product should expose a configurable threshold together with the tradeoff curve, so whoever deploys it can pick the point that suits their context rather than inherit a fixed number.
