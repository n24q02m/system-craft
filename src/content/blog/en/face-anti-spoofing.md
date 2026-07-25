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

<figure class="diagram">
<svg viewBox="0 0 640 258" role="img" aria-label="Four architectures running in parallel over one shared data pipeline and one shared evaluation protocol">
  <defs><marker id="pad-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">ONE INPUT SHARED BY ALL FOUR</text>
  <rect class="box" x="145" y="22" width="350" height="44"/>
  <g text-anchor="middle">
    <text x="320" y="42" font-size="11.5">A face crop, detected and resized</text>
    <text x="320" y="58" font-size="10.5" class="dim">One shared data pipeline</text>
  </g>
  <g class="flow"><path d="M320 66 V78"/><path d="M74 78 H566"/></g>
  <g class="flow" marker-end="url(#pad-a2)">
    <path d="M74 78 V94"/><path d="M238 78 V94"/><path d="M402 78 V94"/><path d="M566 78 V94"/>
  </g>
  <rect class="box" x="0" y="96" width="148" height="72"/>
  <rect class="box" x="164" y="96" width="148" height="72"/>
  <rect class="box" x="328" y="96" width="148" height="72"/>
  <rect class="box" x="492" y="96" width="148" height="72"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="74" y="118">CNN + attention</text>
    <text x="238" y="118">Vision Transformer</text>
    <text x="402" y="118">GAN + aux branch</text>
    <text x="566" y="118">Style vs content</text>
  </g>
  <g text-anchor="middle" font-size="10" class="dim">
    <text x="74" y="136">CBAM after each</text>
    <text x="74" y="150">backbone stage</text>
    <text x="238" y="136">Frozen or</text>
    <text x="238" y="150">fine-tuned backbone</text>
    <text x="402" y="136">The aux branch is</text>
    <text x="402" y="150">the real classifier</text>
    <text x="566" y="136">From scratch, for</text>
    <text x="566" y="150">domain generalization</text>
  </g>
  <g class="flow"><path d="M74 168 V182"/><path d="M238 168 V182"/><path d="M402 168 V182"/><path d="M566 168 V182"/><path d="M74 182 H566"/></g>
  <g class="flow" marker-end="url(#pad-a2)"><path d="M320 182 V198"/></g>
  <rect class="box-accent" x="100" y="200" width="440" height="48"/>
  <g text-anchor="middle">
    <text x="320" y="220" font-size="11.5">One evaluation protocol for all four</text>
    <text x="320" y="236" font-size="10.5" class="dim">which is what makes the results comparable</text>
  </g>
</svg>
<figcaption>Four different approaches only become comparable when they share exactly two things: the data path in and the measurement at the output.</figcaption>
</figure>

### Approach one: a convolutional network with attention

The backbone is a convolutional network pretrained on a large image dataset, used in both a heavy variant for the unconstrained case and a light variant aimed at mobile devices.

The addition is a CBAM attention block inserted after each block group of the backbone. CBAM has two parts in sequence. Channel attention pools the feature map along the spatial axes using both average and max, passes the two resulting vectors through a shared MLP, sums them, and applies a sigmoid to get a weight per channel. Spatial attention pools along the channel axis, runs the result through a 7x7 convolution and a sigmoid to get a weight per location. The point is to let the network learn which channels and which regions deserve attention, instead of treating the whole feature map uniformly.

<figure class="diagram">
<svg viewBox="0 0 640 208" role="img" aria-label="CBAM is two attention steps in sequence: channel attention, then spatial attention">
  <defs><marker id="pad-a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="lbl dim" font-size="9.5">
    <text x="104" y="30">STEP 1 — CHANNEL ATTENTION</text>
    <text x="334" y="30">STEP 2 — SPATIAL ATTENTION</text>
  </g>
  <rect class="box-soft" x="0" y="76" width="88" height="62"/>
  <rect class="box" x="104" y="40" width="214" height="134"/>
  <rect class="box" x="334" y="40" width="214" height="134"/>
  <rect class="box-soft" x="564" y="76" width="76" height="62"/>
  <g text-anchor="middle" font-size="10.5">
    <text x="44" y="96">Input</text>
    <text x="44" y="110">feature</text>
    <text x="44" y="124">map</text>
    <text x="602" y="96">Feature</text>
    <text x="602" y="110">map, now</text>
    <text x="602" y="124">weighted</text>
  </g>
  <rect class="box" x="116" y="50" width="190" height="24"/>
  <rect class="box" x="116" y="80" width="190" height="24"/>
  <rect class="box" x="116" y="110" width="190" height="24"/>
  <rect class="box-accent" x="116" y="140" width="190" height="24"/>
  <rect class="box" x="346" y="50" width="190" height="24"/>
  <rect class="box" x="346" y="80" width="190" height="24"/>
  <rect class="box" x="346" y="110" width="190" height="24"/>
  <rect class="box-accent" x="346" y="140" width="190" height="24"/>
  <g text-anchor="middle" font-size="10.5">
    <text x="211" y="66">Pool along the spatial axes</text>
    <text x="211" y="96">with average and max</text>
    <text x="211" y="126">Shared MLP, then sum</text>
    <text x="211" y="156">One weight per channel</text>
    <text x="441" y="66">Pool along the channel axis</text>
    <text x="441" y="96">with average and max</text>
    <text x="441" y="126">7x7 convolution, sigmoid</text>
    <text x="441" y="156">One weight per location</text>
  </g>
  <g class="flow" marker-end="url(#pad-a3)">
    <path d="M88 107 H104"/><path d="M318 107 H334"/><path d="M548 107 H564"/>
    <path d="M211 74 V80"/><path d="M211 104 V110"/><path d="M211 134 V140"/>
    <path d="M441 74 V80"/><path d="M441 104 V110"/><path d="M441 134 V140"/>
  </g>
  <text x="0" y="194" font-size="10.5" class="dim">Two steps in sequence: which channels deserve attention, then which regions do.</text>
</svg>
<figcaption>Each step collapses exactly one axis in order to ask one question: the first drops the spatial axes to ask about channels, the second drops the channel axis to ask about locations.</figcaption>
</figure>

The classification head after the backbone is global average pooling, dropout, an intermediate linear layer, batch normalization, ReLU, and a final linear layer returning a single logit.

### Approach two: Vision Transformer

This one swaps the convolutional backbone for a pretrained Vision Transformer, in both a full-size and a very small variant. The image is split into patches, and the representation used for classification comes from the CLS token, feeding a head similar to the one above.

It also has a mode that freezes the entire backbone and trains only the head. That is cheap and reasonable when data is scarce, but it comes with a tradeoff discussed in the background section below.

### Approach three: a GAN with an auxiliary classification branch

This approach uses a generative adversarial network. The generator follows the DCGAN pattern: a latent vector goes through a stack of upsampling and convolution layers to build an image. The discriminator has four stride-2 convolutional blocks with CBAM inserted, then splits into two branches — one judging whether an image is real or generated, which serves the adversarial objective, and an auxiliary one classifying live versus spoof.

<figure class="diagram">
<svg viewBox="0 0 640 236" role="img" aria-label="The discriminator splits into an adversarial branch and an auxiliary branch, and the auxiliary one is the classifier that actually gets used">
  <defs><marker id="pad-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="26" font-size="9.5">HOW IMAGES REACH THE DISCRIMINATOR</text>
  <rect class="box" x="0" y="36" width="112" height="36"/>
  <rect class="box" x="128" y="36" width="112" height="36"/>
  <rect class="box" x="256" y="36" width="148" height="36"/>
  <rect class="box-soft" x="256" y="94" width="148" height="36"/>
  <rect class="box" x="430" y="36" width="210" height="94"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="56" y="58">Latent vector</text>
    <text x="184" y="58">Generator</text>
    <text x="330" y="58">Generated image</text>
    <text x="330" y="116">Real images</text>
  </g>
  <text x="442" y="58" font-size="11.5">Discriminator</text>
  <g font-size="10" class="dim">
    <text x="442" y="78">Four stride-2 conv blocks</text>
    <text x="442" y="92">with CBAM inserted,</text>
    <text x="442" y="106">then it splits in two</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="0" y="104">Real images carry</text>
    <text x="0" y="118">their live/spoof label</text>
  </g>
  <g class="flow" marker-end="url(#pad-a4)">
    <path d="M112 54 H128"/><path d="M240 54 H256"/><path d="M404 54 H430"/><path d="M404 112 H430"/>
    <path d="M342 146 V160"/><path d="M544 146 V160"/>
  </g>
  <g class="flow"><path d="M535 130 V146"/><path d="M342 146 H544"/></g>
  <text class="lbl dim" x="0" y="152" font-size="9.5">THE TWO OUTPUTS OF THE DISCRIMINATOR</text>
  <rect class="box" x="252" y="160" width="180" height="64"/>
  <rect class="box-accent" x="448" y="160" width="192" height="64"/>
  <g text-anchor="middle">
    <text x="342" y="180" font-size="11.5">Adversarial branch</text>
    <text x="342" y="198" font-size="10" class="dim">Real or generated?</text>
    <text x="342" y="212" font-size="10" class="dim">A training signal only</text>
    <text x="544" y="180" font-size="11.5">Auxiliary branch</text>
    <text x="544" y="198" font-size="10" class="dim">Live or spoof?</text>
    <text x="544" y="212" font-size="10" class="dim">The classifier actually used</text>
  </g>
</svg>
<figcaption>The generated images are not the goal. The adversarial part exists only to force the discriminator into a representation rich enough for the branch beside it to use.</figcaption>
</figure>

The detail worth noting is that the auxiliary branch is the classifier that actually gets used. The adversarial part is a supplementary training signal, there to force the discriminator to learn an informative representation of face images; the generated images themselves are not the goal. That part is trained as a Wasserstein GAN with gradient penalty, a variant chosen for being more stable than the original adversarial formulation.

### Approach four: separating style from content

The three approaches above all start from an off-the-shelf architecture. The fourth goes the other way: a network implemented from scratch and designed specifically for domain generalization, meaning the ability to work on a data source it has never seen.

The underlying idea is to split an image into two components. "Content" is what says whether this is a real person or a copy. "Style" is what reflects which camera, which lighting, which post-processing. The goal is to force the content representation to be independent of the style.

The structure has the following parts:

- A hand-designed multi-stage feature extractor, with no pretrained backbone.
- A content branch and a style branch. The style branch goes through instance normalization and a few fully-connected layers to produce two parameters: a scale and a shift.
- A recombination step using AdaIN, adaptive instance normalization: normalize the content features to zero mean and unit variance, then apply the two style parameters.

The core mechanism is how the training pairs are generated. Within each batch the sample order is shuffled, so the style of one image gets grafted onto the content of another. That hybrid pair is labeled positive if the two source images share a live/spoof class and negative if they do not. A contrastive loss over these pairs pushes the network to place same-class images close together regardless of which device they came from — exactly what is needed when deploying onto unfamiliar hardware.

<figure class="diagram">
<svg viewBox="0 0 640 280" role="img" aria-label="Features split into content and style, are recombined through AdaIN, and hybrid pairs come from shuffling the sample order within a batch">
  <defs><marker id="pad-a5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">SEPARATING CONTENT FROM STYLE</text>
  <rect class="box-soft" x="0" y="58" width="104" height="30"/>
  <rect class="box" x="120" y="49" width="132" height="48"/>
  <rect class="box" x="268" y="35" width="150" height="30"/>
  <rect class="box" x="268" y="81" width="150" height="30"/>
  <rect class="box" x="434" y="20" width="206" height="60"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="52" y="77">Input image</text>
    <text x="186" y="69">Feature</text>
    <text x="186" y="85">extractor</text>
    <text x="343" y="54">Style branch</text>
    <text x="343" y="100">Content branch</text>
  </g>
  <text x="446" y="40" font-size="11.5">Instance normalization</text>
  <g font-size="10" class="dim">
    <text x="446" y="56">then fully-connected layers</text>
    <text x="446" y="70">producing a scale and a shift</text>
  </g>
  <g class="flow"><path d="M252 73 H262"/><path d="M262 50 V96"/></g>
  <g class="flow" marker-end="url(#pad-a5)">
    <path d="M104 73 H120"/><path d="M262 50 H268"/><path d="M262 96 H268"/><path d="M418 50 H434"/>
    <path d="M343 111 V130"/><path d="M537 80 V130"/><path d="M370 192 V212"/>
  </g>
  <text class="lbl dim" x="0" y="126" font-size="9.5">RECOMBINING WITH AdaIN</text>
  <rect class="box" x="180" y="130" width="380" height="62"/>
  <text x="192" y="150" font-size="11.5">AdaIN normalizes the content features</text>
  <g font-size="10.5" class="dim">
    <text x="192" y="166">to zero mean and unit variance,</text>
    <text x="192" y="180">then applies the style scale and shift</text>
  </g>
  <text class="lbl dim" x="0" y="206" font-size="9.5">SHUFFLING WITHIN THE BATCH</text>
  <rect class="box-accent" x="0" y="212" width="640" height="60"/>
  <text x="12" y="232" font-size="11.5">In-batch shuffling grafts the style of one image onto the content of another</text>
  <g font-size="10.5" class="dim">
    <text x="12" y="248">The hybrid pair is positive if the two sources share a live/spoof class, negative otherwise</text>
    <text x="12" y="262">A contrastive loss over these pairs pulls same-class images together regardless of device</text>
  </g>
</svg>
<figcaption>Shuffling manufactures samples that do not exist in the data: the same content wearing another device's style. That is how you tell a network the device is not the thing to learn.</figcaption>
</figure>

Two more details. The output is not a single logit but a depth map built through upsampling layers: a real face has three-dimensional structure, while a printed photo or a replayed screen is essentially flat, so depth is a richer supervision signal than a binary label. And there is a domain discriminator branch attached through a gradient reversal layer: that branch tries to guess which data source a sample came from, and the reversal pushes the feature extractor in the opposite direction, toward a representation from which the source cannot be guessed.

<figure class="diagram">
<svg viewBox="0 0 640 148" role="img" aria-label="A gradient reversal layer passes features through unchanged going forward and negates the gradient coming back">
  <defs><marker id="pad-a6" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">UNCHANGED GOING FORWARD, NEGATED COMING BACK</text>
  <rect class="box" x="0" y="30" width="150" height="56"/>
  <rect class="box-accent" x="245" y="30" width="150" height="56"/>
  <rect class="box" x="490" y="30" width="150" height="56"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="75" y="50">Feature</text>
    <text x="75" y="66">extractor</text>
    <text x="320" y="50">Gradient</text>
    <text x="320" y="66">reversal</text>
    <text x="565" y="50">Domain</text>
    <text x="565" y="66">discriminator</text>
  </g>
  <g class="flow" marker-end="url(#pad-a6)">
    <path d="M150 46 H245"/><path d="M395 46 H490"/>
    <path d="M245 70 H150"/><path d="M490 70 H395"/>
  </g>
  <g text-anchor="middle" font-size="10" class="dim">
    <text x="197" y="40">forward</text>
    <text x="442" y="40">forward</text>
    <text x="197" y="84">backward</text>
    <text x="442" y="84">backward</text>
  </g>
  <text text-anchor="middle" x="320" y="108" font-size="10.5" class="dim">At this layer the backward gradient is multiplied by a negative number.</text>
  <text x="0" y="130" font-size="10.5" class="dim">The extractor is therefore pushed toward features from which the domain branch cannot guess the source.</text>
</svg>
<figcaption>Both branches optimize the same loss, but the flipped sign makes them pull in opposite directions — that is the whole trick.</figcaption>
</figure>

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

<figure class="diagram">
<svg viewBox="0 0 640 262" role="img" aria-label="Four evaluation scenarios arranged as a staircase of increasing difficulty, from within one dataset to a source never seen">
  <defs><marker id="pad-a7" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="lbl dim" font-size="9.5">
    <text x="480" y="44">LEVEL 4</text>
    <text x="320" y="80">LEVEL 3</text>
    <text x="160" y="116">LEVEL 2</text>
    <text x="0" y="152">LEVEL 1</text>
  </g>
  <g font-size="10">
    <text x="480" y="60">Train: multiple sources</text>
    <text x="480" y="74">Test: an unseen source</text>
    <text x="320" y="96">Train: several datasets</text>
    <text x="320" y="110">Test: an entirely different one</text>
    <text x="160" y="132">Train: a mixture of sets</text>
    <text x="160" y="146">Test: the held-out part</text>
    <text x="0" y="168">Train: one dataset</text>
    <text x="0" y="182">Test: that same dataset</text>
  </g>
  <rect class="box-accent" x="480" y="88" width="160" height="12"/>
  <rect class="box" x="320" y="124" width="160" height="12"/>
  <rect class="box" x="160" y="160" width="160" height="12"/>
  <rect class="box-soft" x="0" y="196" width="160" height="12"/>
  <g class="edge"><path d="M160 196 V172"/><path d="M320 160 V136"/><path d="M480 124 V100"/></g>
  <g class="flow" marker-end="url(#pad-a7)"><path d="M120 222 H630"/></g>
  <text class="lbl dim" x="0" y="226" font-size="9.5">DIFFICULTY INCREASES</text>
  <text x="0" y="250" font-size="10.5" class="dim">The information is in the gap between levels, not in the result at the easiest one.</text>
</svg>
<figcaption>Each level removes one advantage the level below still enjoys. The top one lets the model get acquainted with nothing at all beforehand.</figcaption>
</figure>

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

<figure class="diagram">
<svg viewBox="0 0 640 260" role="img" aria-label="Two overlapping score distributions cut by a threshold line, producing a region of attacks that get through and a region of genuine users rejected">
  <defs>
    <marker id="pad-b" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker>
    <marker id="pad-c" markerWidth="8" markerHeight="8" refX="1" refY="4" orient="auto">
      <path d="M8,0 L0,4 L8,8 z" fill="currentColor"/></marker>
  </defs>
  <path class="area-warn" d="M200 190 C 252.3 190 285.6 150.7 319.9 120.4 L319.9 190 Z"/>
  <path class="area" d="M320.1 115 C 354.4 147.6 387.7 190 440 190 L320.1 190 Z"/>
  <path class="curve-accent" d="M60 190 C 145 190 180 78 250 78 C 320 78 355 190 440 190"/>
  <path class="curve-warn" d="M200 190 C 285 190 320 86 390 86 C 460 86 495 190 580 190"/>
  <path class="axis" d="M40 190 H620"/>
  <path class="edge dashed" d="M320 56 V190"/>
  <path class="flow" d="M270 50 H370" marker-start="url(#pad-c)" marker-end="url(#pad-b)"/>
  <text text-anchor="middle" x="320" y="30" font-size="10.5" class="dim">decision threshold</text>
  <text text-anchor="middle" x="320" y="68" font-size="10" class="dim">moving it trades one area for the other</text>
  <g text-anchor="middle" font-size="11">
    <text x="150" y="152">Genuine</text>
    <text x="490" y="152">Attacks</text>
  </g>
  <g font-size="10" class="dim">
    <text x="0" y="204">low score — looks genuine</text>
    <text text-anchor="end" x="636" y="204">high score — looks like an attack</text>
  </g>
  <rect class="box-warn" x="0" y="215" width="10" height="10"/>
  <rect class="cell-on" x="300" y="215" width="10" height="10"/>
  <g font-size="10.5" class="dim">
    <text x="16" y="224">Attacks passing the threshold — APCER</text>
    <text x="316" y="224">Genuine users rejected — BPCER</text>
  </g>
  <text x="0" y="246" font-size="10.5" class="dim">Model quality is how much the two distributions overlap; the threshold is only an operating parameter chosen later.</text>
</svg>
<figcaption>Moving the threshold only shifts error from one region into the other. Shrinking both at once means pulling the two distributions apart, which means changing the model.</figcaption>
</figure>

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
