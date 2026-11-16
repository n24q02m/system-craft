---
title: "Vehicle detection and the road down to the edge"
description: "Detecting vehicles in bad weather on constrained hardware: two-tier augmentation, knowledge distillation, and the path down to the device."
lang: "en"
order: 4
field: "DET"
topics: ["object detection", "knowledge distillation", "mAP", "edge deployment", "augmentation"]
---

A traffic camera points down at the road and produces a continuous stream of frames. The job is to take each frame and work out which vehicles are in it, what type each one is, and where it sits in the image. This is object detection, one of the most heavily studied problems in computer vision, and for daytime footage in clear weather the models already available handle it well.

The difficulty comes from two constraints that ride along with it. First, the system has to work in exactly the conditions that standard datasets rarely contain: rain, night, headlight glare in the lens, fog. Second, the model has to run on a device out in the field rather than on a GPU server, which means a budget on parameter count, a budget on memory, and CPU only.

These two constraints pull in opposite directions. Handling bad conditions usually calls for a stronger model and more varied data; running on the edge calls for a smaller one. Most of the engineering work lives in reconciling them.

## The system as built

### The data and the four classes to separate

The data is imagery from real traffic cameras. Labels were initially split by day and night condition, then collapsed into four shared classes: motorcycle, car, bus, truck. The merge had a practical reason. A car at night is still a car, and splitting classes by time of day only thins out the data behind each one.

The class distribution is heavily skewed. Motorcycles dominate by count, buses are sparse, and the gap between the most common class and the rarest is wide enough that any aggregate metric is driven by the majority class. This is not a flaw in the collection; it is an accurate reflection of the traffic. It has to be handled at the level of method and reporting, not by collecting more data.

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="Bar chart of the four vehicle classes, motorcycles dominate and buses are sparse">
  <text class="lbl dim" x="0" y="14" font-size="9.5">COUNT BY CLASS</text>
  <path class="axis" d="M0 30 V170 H316"/>
  <rect class="bar-accent" x="14" y="46" width="56" height="124"/>
  <rect class="bar" x="92" y="114" width="56" height="56"/>
  <rect class="bar" x="170" y="151" width="56" height="19"/>
  <rect class="bar" x="248" y="162" width="56" height="8"/>
  <g font-size="10.5" text-anchor="middle">
    <text x="42" y="186">motorcycle</text>
    <text x="120" y="186">car</text>
    <text x="198" y="186">truck</text>
    <text x="276" y="186">bus</text>
  </g>
  <rect class="box-soft" x="348" y="44" width="292" height="96"/>
  <text x="358" y="64" font-size="11.5">Aggregates follow the majority class</text>
  <g font-size="10" class="dim">
    <text x="358" y="80">A mean over the four classes mostly</text>
    <text x="358" y="94">reflects the motorcycle class alone.</text>
    <text x="358" y="108">Seeing where the rarest class sits</text>
    <text x="358" y="122">requires per-class reporting.</text>
  </g>
</svg>
<figcaption>This long-tailed shape is why a single aggregate number does not describe the result.</figcaption>
</figure>

There is also a step that generates object-free background images through inpainting: take a real frame, erase the vehicles, and let the algorithm fill the hole back in with plausible background. These serve as negative examples, teaching the model that an empty stretch of road has nothing to report.

### Two-tier augmentation

Data augmentation is split into two tiers, and the boundary between them is a deliberate design decision.

The offline tier runs before training, through a dedicated image transformation library, and writes its results to disk as images. The transforms cover horizontal flips; shifts, rotations and scaling; colour and brightness changes; blur; added noise. The most important group is the weather simulations: rain, fog, snow, cast shadows, sun flare. That group maps directly onto the bad-conditions requirement, and it is also the most expensive to compute.

The on-the-fly tier, meaning the augmentation built into the training framework, is almost entirely switched off. What remains is mosaic, which stitches four images into one so the model sees several contexts and several scales in a single sample, along with random erasing of an image region.

The split comes out of a specific trade-off. Generating variants during training is the default in most frameworks because the model sees a different variant every epoch, so it buys more regularisation for the same storage. But the weather simulations are expensive, and paying that cost every epoch is waste; computing them once and caching them is far cheaper.

The risk of running both tiers at once is equally specific: distortions compound. An image already baked with rain and reduced brightness, if it then picks up a colour shift and a blur at training time, can drift away from any frame a real camera would ever record. Picking one tier as primary and writing down why is how you avoid that.

<figure class="diagram">
<svg viewBox="0 0 640 242" role="img" aria-label="Two augmentation tiers, an offline tier that runs once and an on-the-fly tier that is almost entirely off, with a warning about compounding distortion">
  <text class="lbl dim" x="0" y="14" font-size="9.5">OFFLINE TIER</text>
  <text class="lbl dim" x="340" y="14" font-size="9.5">ON-THE-FLY TIER</text>
  <rect class="box" x="0" y="24" width="300" height="64"/>
  <rect class="box" x="340" y="24" width="300" height="64"/>
  <rect class="box-accent" x="0" y="96" width="300" height="52"/>
  <rect class="box-soft" x="340" y="96" width="300" height="52"/>
  <g font-size="11.5">
    <text x="10" y="44">Runs once before training</text>
    <text x="350" y="44">A different variant every epoch</text>
    <text x="10" y="116">Weather simulation</text>
    <text x="350" y="116">Only two transforms left</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="60">flips, shifts, rotation, colour, blur, noise</text>
    <text x="10" y="74">results written to disk as images</text>
    <text x="350" y="60">cheap, and better regularisation per byte stored</text>
    <text x="350" y="74">but here it is almost entirely switched off</text>
    <text x="10" y="132">rain, fog, snow, cast shadows, sun flare</text>
    <text x="350" y="132">mosaic and random erasing of a region</text>
  </g>
  <text class="lbl dim" x="0" y="164" font-size="9.5">RISK OF RUNNING BOTH TIERS</text>
  <rect class="box-warn" x="0" y="172" width="640" height="66"/>
  <text x="10" y="192" font-size="11.5">Run both tiers at once and the distortions compound</text>
  <g font-size="10" class="dim">
    <text x="10" y="208">An image already baked with rain and reduced brightness, if it then picks up a colour shift and a</text>
    <text x="10" y="222">blur at training time, can drift away from any frame a real camera would ever record.</text>
  </g>
</svg>
<figcaption>The boundary between the two tiers is a design decision, not a framework default.</figcaption>
</figure>

### The student-teacher architecture

The model size constraint is handled with knowledge distillation, with two models playing two roles.

**The teacher** is a large object detector from the YOLO family, fine-tuned from weights pre-trained on a general-purpose image set. Its only job is to be a source of supervisory signal; it is never deployed.

**The student** is a custom architecture defined through a config file, with three changes relative to the stock design:

- Every standard convolution is replaced with a depthwise separable convolution, or a Ghost variant. This is where most of the parameter reduction comes from.
- A detection head is added at a higher resolution, giving four heads instead of three. Vehicles far down the frame in a traffic camera view occupy very few pixels, and a higher-resolution head gives the model a chance to catch them.
- No attention modules at all. This is a deliberate constraint: attention blocks add latency and tend to be poorly supported on mobile runtimes, so they were ruled out at design time.

<figure class="diagram">
<svg viewBox="0 0 640 248" role="img" aria-label="Four detection heads ordered by resolution, with the fourth and highest-resolution head marked as the addition to the stock three-head design">
  <defs><marker id="det-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">FOUR DETECTION HEADS, HIGH TO LOW</text>
  <rect class="box" x="0" y="24" width="36" height="36"/>
  <rect class="box" x="0" y="72" width="36" height="36"/>
  <rect class="box" x="0" y="120" width="36" height="36"/>
  <rect class="box" x="0" y="168" width="36" height="36"/>
  <path class="grid" d="M6 24 V60 M12 24 V60 M18 24 V60 M24 24 V60 M30 24 V60 M0 30 H36 M0 36 H36 M0 42 H36 M0 48 H36 M0 54 H36"/>
  <path class="grid" d="M9 72 V108 M18 72 V108 M27 72 V108 M0 81 H36 M0 90 H36 M0 99 H36"/>
  <path class="grid" d="M12 120 V156 M24 120 V156 M0 132 H36 M0 144 H36"/>
  <path class="grid" d="M18 168 V204 M0 186 H36"/>
  <g class="flow" marker-end="url(#det-a4)">
    <path d="M36 42 H72"/>
    <path d="M36 90 H72"/>
    <path d="M36 138 H72"/>
    <path d="M36 186 H72"/>
  </g>
  <rect class="box-accent" x="76" y="24" width="564" height="36"/>
  <rect class="box" x="76" y="72" width="564" height="36"/>
  <rect class="box" x="76" y="120" width="564" height="36"/>
  <rect class="box" x="76" y="168" width="564" height="36"/>
  <g font-size="11.5">
    <text x="86" y="47">Highest resolution, added</text>
    <text x="86" y="95">High resolution</text>
    <text x="86" y="143">Medium resolution</text>
    <text x="86" y="191">Low resolution</text>
  </g>
  <g font-size="10" class="dim">
    <text x="290" y="47">the fourth head, absent from the stock three-head design</text>
    <text x="290" y="95">distant vehicles, very few pixels across</text>
    <text x="290" y="143">vehicles in the middle of the frame</text>
    <text x="290" y="191">near vehicles, covering many pixels</text>
  </g>
  <text x="0" y="224" font-size="10.5" class="dim">The higher the resolution, the fewer image pixels each feature cell covers, so small objects leave a trace.</text>
  <text x="0" y="240" font-size="10.5" class="dim">The three stock heads cover medium and large objects; vehicles at the far end of the frame fall through.</text>
</svg>
<figcaption>The price of the fourth head is extra compute at the most expensive resolution in the network.</figcaption>
</figure>

Distillation keeps the teacher frozen. The loss has two parts: the ordinary detection term computed against ground truth, plus a distillation term based on the KL divergence between the student's output distribution and the teacher's. That second part has two knobs, temperature, which softens the distribution so low-probability classes still contribute signal, and a mixing coefficient, which decides how much the student listens to the ground truth against how much it listens to the teacher.

### Inference and preprocessing

The system supports two inference modes. The standard mode pushes the whole frame through the model once. The tiled mode splits a large image into overlapping cells, runs the model on each cell, and merges the results. This costs several times the compute, but it makes small objects large relative to the model's input, so it catches distant vehicles that the standard mode misses. The overlap exists so that a vehicle straddling the boundary between two cells does not get cut in half.

<figure class="diagram">
<svg viewBox="0 0 640 240" role="img" aria-label="Tiled mode splits the frame into overlapping cells, compared with feeding the whole frame into the same model input size">
  <text class="lbl dim" x="0" y="14" font-size="9.5">TILED MODE</text>
  <text class="lbl dim" x="380" y="14" font-size="9.5">THE SAME MODEL INPUT</text>
  <path class="grid" d="M360 6 V218"/>
  <rect class="area" x="100" y="24" width="30" height="140"/>
  <rect class="area" x="200" y="24" width="30" height="140"/>
  <rect class="area" x="0" y="80" width="330" height="28"/>
  <rect class="box" x="0" y="24" width="130" height="84"/>
  <rect class="box" x="100" y="24" width="130" height="84"/>
  <rect class="box" x="200" y="24" width="130" height="84"/>
  <rect class="box" x="0" y="80" width="130" height="84"/>
  <rect class="box" x="100" y="80" width="130" height="84"/>
  <rect class="box" x="200" y="80" width="130" height="84"/>
  <path class="edge dashed" d="M115 24 V164"/>
  <rect class="box-accent" x="102" y="118" width="26" height="14"/>
  <rect class="box" x="380" y="38" width="120" height="62"/>
  <rect class="box-accent" x="430" y="74" width="24" height="11"/>
  <rect class="box" x="380" y="124" width="120" height="62"/>
  <rect class="box-accent" x="436" y="160" width="9" height="6"/>
  <g font-size="10" class="dim">
    <text x="516" y="66">one tile</text>
    <text x="516" y="152">the whole frame</text>
    <text x="0" y="182">the shaded strips are where the cells overlap</text>
    <text x="0" y="196">the dashed line is the cut without any overlap</text>
    <text x="0" y="210">a vehicle across it stays whole inside one cell</text>
    <text x="380" y="204">the distant object is far larger with one tile</text>
  </g>
  <text x="0" y="232" font-size="10.5" class="dim">The trade-off: tiled mode costs several times the compute for every frame.</text>
</svg>
<figcaption>The overlap is why a vehicle straddling the boundary between two cells is not cut in half.</figcaption>
</figure>

There is also an optional preprocessing step, made up of adaptive histogram equalisation, denoising and sharpening, aimed at underexposed or low-contrast frames. And there is post-training dynamic quantisation applied to the linear layers, trading some accuracy for size and speed.

### Getting it onto the device

Deployment is a separate Android application. It uses a lightweight inference runtime built for mobile, paired with a computer vision library for image loading and post-processing, with the Java layer talking to the C++ compute through JNI. Everything runs on the CPU, with no dependency on whether the device happens to have a hardware accelerator.

The model is packaged in that runtime's own format, a pair of files, one describing the network structure and one holding the weights, placed in the application's asset directory. The conversion from the training framework's format into that pair of files is a link in the chain of its own, and as the end of this post argues, it has to be tested as one.

## Background

<figure class="diagram">
<svg viewBox="0 0 640 196" role="img" aria-label="Knowledge distillation flow from a teacher model to a student model and down onto the device">
  <defs><marker id="det-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">OFFLINE</text>
    <text class="lbl" x="452" y="14" font-size="9.5">ON DEVICE</text>
  </g>
  <rect class="box" x="0" y="26" width="172" height="48"/>
  <rect class="box" x="0" y="104" width="172" height="48"/>
  <rect class="box-accent" x="234" y="64" width="178" height="52"/>
  <rect class="box" x="452" y="64" width="188" height="52"/>
  <g class="flow" marker-end="url(#det-a)">
    <path d="M172 50 H206 V84 H228"/>
    <path d="M172 128 H206 V98 H228"/>
    <path d="M412 90 H446"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="48">Teacher model</text>
    <text x="10" y="126">Ground truth</text>
    <text x="244" y="84">Student model</text>
    <text x="462" y="84">Mobile runtime</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="64">large, accurate, not deployed</text>
    <text x="10" y="142">from the labelled data</text>
    <text x="244" y="100">depthwise separable convolutions</text>
    <text x="244" y="112">four heads, no attention blocks</text>
    <text x="462" y="100">runs on CPU only</text>
    <text x="462" y="112">no hardware acceleration needed</text>
  </g>
  <text x="0" y="176" font-size="10.5" class="dim">The student loss combines a detection term on ground truth with a distillation term on the teacher output.</text>
  <text x="0" y="192" font-size="10.5" class="dim">The format conversion into the runtime is its own link in the chain, and needs its own test.</text>
</svg>
<figcaption>The teacher serves only as a source of supervisory signal and is never deployed.</figcaption>
</figure>

### Measuring object detection: IoU and why one threshold is not enough

A prediction in this problem is a bounding box plus a class label. To decide whether that prediction is right, you compare the predicted box against the true box using intersection over union: the area the two share divided by the area they cover together, IoU for short. A value of one means an exact overlap; zero means they are disjoint.

The question is where to put the acceptance threshold. A low threshold is lenient about localisation, so a box that is noticeably off still counts as correct. A high threshold demands tight localisation. Picking a single threshold means silently deciding on behalf of every downstream application, and a system that counts vehicles has very different localisation requirements from one that estimates distance. The way the current standard resolves this is to average over several thresholds.

<figure class="diagram">
<svg viewBox="0 0 640 258" role="img" aria-label="Intersection over union of two bounding boxes, and three overlap levels placed on an IoU scale with two threshold marks">
  <text class="lbl dim" x="0" y="14" font-size="9.5">INTERSECTION OVER UNION</text>
  <text class="lbl dim" x="330" y="14" font-size="9.5">ONE THRESHOLD IS NOT ENOUGH</text>
  <path class="grid" d="M314 6 V218"/>
  <rect class="area" x="86" y="76" width="56" height="58"/>
  <rect class="box" x="24" y="48" width="118" height="86"/>
  <rect class="box" x="86" y="76" width="118" height="86"/>
  <path class="edge dashed" d="M19 43 H147 V71 H209 V167 H81 V139 H19 Z"/>
  <g font-size="10" class="dim">
    <text x="24" y="36">true box</text>
    <text x="216" y="62">union area</text>
    <text x="216" y="76">dashed outline</text>
    <text x="86" y="180">predicted box</text>
  </g>
  <text x="114" y="109" font-size="10" text-anchor="middle">shared</text>
  <text x="0" y="200" font-size="10.5" class="dim">the shared area divided by the area they cover together</text>
  <text x="0" y="214" font-size="10.5" class="dim">one means an exact overlap, zero means disjoint</text>
  <g font-size="10" class="dim">
    <text x="330" y="38">small overlap</text>
    <text x="436" y="38">medium overlap</text>
    <text x="542" y="38">large overlap</text>
  </g>
  <rect class="area" x="368" y="50" width="14" height="34"/>
  <rect class="area" x="460" y="50" width="28" height="34"/>
  <rect class="area" x="552" y="50" width="42" height="34"/>
  <rect class="box" x="330" y="44" width="52" height="40"/>
  <rect class="box" x="368" y="50" width="52" height="40"/>
  <rect class="box" x="436" y="44" width="52" height="40"/>
  <rect class="box" x="460" y="50" width="52" height="40"/>
  <rect class="box" x="542" y="44" width="52" height="40"/>
  <rect class="box" x="552" y="50" width="52" height="40"/>
  <g class="edge">
    <path d="M375 96 V104 H435 V120"/>
    <path d="M474 96 V104 H510 V120"/>
    <path d="M573 96 V104 H570 V120"/>
  </g>
  <path class="axis" d="M330 124 H630 M330 124 V130 M480 124 V130 M555 124 V130 M630 124 V130"/>
  <path class="grid dashed" d="M480 106 V124 M555 106 V124"/>
  <circle class="node-open" cx="435" cy="124" r="3.2"/>
  <circle class="node" cx="510" cy="124" r="3.2"/>
  <circle class="node-accent" cx="570" cy="124" r="3.2"/>
  <g class="dim" text-anchor="middle">
    <text class="num" x="330" y="140">0</text>
    <text class="num" x="480" y="140">0.5</text>
    <text class="num" x="555" y="140">0.75</text>
    <text class="num" x="630" y="140">1</text>
  </g>
  <text x="330" y="160" font-size="10" class="dim">IoU of the pair, from disjoint to exact overlap</text>
  <text x="330" y="176" font-size="10" class="dim">The middle pair: correct at 0.5, wrong at 0.75.</text>
  <text x="0" y="234" font-size="10.5" class="dim">Picking a single threshold silently decides on behalf of every application downstream.</text>
  <text x="0" y="250" font-size="10.5" class="dim">The current standard averages over ten thresholds from 0.5 to 0.95 to avoid exactly that.</text>
</svg>
<figcaption>Which is why a result quoted at one threshold and a result quoted at another are not directly comparable.</figcaption>
</figure>

### Knowledge distillation and the dark knowledge intuition

Knowledge distillation trains a small model to match not only the ground truth labels but also the output distribution of a larger model that has already finished training.

The intuition is about how much information each signal carries. A hard label says only "this is a motorcycle", one bit about the correct class and nothing more. The teacher's output distribution says "this is a motorcycle, somewhat similar to a bicycle, and almost certainly not a bus". That relational structure between classes, sometimes called dark knowledge, is what hard labels do not carry, and it is why a student learns faster from a teacher than from labels alone.

<figure class="diagram">
<svg viewBox="0 0 640 222" role="img" aria-label="Two bar charts, a hard label puts everything on one class while the teacher distribution spreads value onto similar classes">
  <text class="lbl dim" x="0" y="14" font-size="9.5">HARD LABEL</text>
  <text class="lbl dim" x="346" y="14" font-size="9.5">TEACHER DISTRIBUTION</text>
  <path class="grid" d="M320 6 V178"/>
  <path class="axis" d="M0 40 V152 H280"/>
  <path class="axis" d="M346 40 V152 H626"/>
  <rect class="bar-accent" x="16" y="48" width="46" height="104"/>
  <rect class="bar-accent" x="362" y="52" width="46" height="100"/>
  <rect class="bar" x="430" y="114" width="46" height="38"/>
  <rect class="bar" x="498" y="139" width="46" height="13"/>
  <rect class="bar" x="566" y="147" width="46" height="5"/>
  <g font-size="10" text-anchor="middle">
    <text x="39" y="168">motorcycle</text>
    <text x="107" y="168">bicycle</text>
    <text x="175" y="168">car</text>
    <text x="243" y="168">bus</text>
    <text x="385" y="168">motorcycle</text>
    <text x="453" y="168">bicycle</text>
    <text x="521" y="168">car</text>
    <text x="589" y="168">bus</text>
  </g>
  <text x="0" y="192" font-size="10.5" class="dim">One correct class, the other three at zero.</text>
  <text x="346" y="192" font-size="10.5" class="dim">The similar class still carries real weight.</text>
  <text x="0" y="214" font-size="10.5" class="dim">The relational structure between classes is what hard labels do not carry, and what the student learns.</text>
</svg>
<figcaption>The temperature knob in the distillation loss is exactly what controls how soft the right-hand distribution is.</figcaption>
</figure>

### Why distillation for detection differs from distillation for classification

The technique was invented for image classification and does not transfer straight across to detection, for three reasons.

First, most of the area in a frame is background. Force the student to imitate the teacher across the entire feature map and almost all of the learned signal will be about background, which nobody cares about.

Second, detection has a coordinate regression component, not just classification. Forcing the student to match the teacher exactly on coordinates can backfire when the teacher itself is off.

Third, the imbalance between background and objects is far more severe than ordinary class imbalance in classification, so the loss needs a mechanism to compensate.

### The trade-off between accuracy and size

There are two main levers for shrinking a model. Depthwise separable convolution splits a standard convolution into two steps, a per-channel filter followed by a channel mixing step through a 1x1 convolution, cutting the number of multiplications and parameters by a large factor at the cost of each layer being slightly less expressive. Quantisation represents weights as low-width integers rather than floats, reducing size and speeding things up on hardware with integer support, at the cost of some numerical resolution.

<figure class="diagram">
<svg viewBox="0 0 640 240" role="img" aria-label="A standard convolution does one operation, while a separable convolution filters each channel and then mixes channels with a one by one convolution">
  <defs><marker id="det-a8" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">STANDARD CONVOLUTION</text>
  <text class="lbl dim" x="340" y="14" font-size="9.5">SEPARABLE CONVOLUTION</text>
  <rect class="box" x="0" y="24" width="300" height="80"/>
  <rect class="box" x="340" y="24" width="300" height="32"/>
  <rect class="box" x="340" y="72" width="300" height="32"/>
  <path class="flow" marker-end="url(#det-a8)" d="M490 58 V70"/>
  <text x="10" y="44" font-size="11.5">One single operation</text>
  <g font-size="10" class="dim">
    <text x="10" y="60">filters space and mixes channels at once</text>
    <text x="10" y="74">every filter touches every input channel</text>
    <text x="10" y="88">no separate steps involved</text>
  </g>
  <g font-size="11.5">
    <text x="350" y="44">Step one: filter each channel</text>
    <text x="350" y="92">Step two: mix channels with 1x1</text>
  </g>
  <text class="lbl dim" x="0" y="126" font-size="9.5">MULTIPLICATIONS, SHOWN AS AREA</text>
  <rect class="box-soft" x="0" y="132" width="280" height="48"/>
  <rect class="box-accent" x="340" y="132" width="14" height="48"/>
  <rect class="box-accent" x="372" y="132" width="52" height="48"/>
  <g font-size="10" class="dim">
    <text x="0" y="194">filter and mix at once</text>
    <text x="340" y="194">filter</text>
    <text x="372" y="194">mix channels</text>
  </g>
  <text x="0" y="216" font-size="10.5" class="dim">Splitting into two steps cuts multiplications and parameters by a large factor.</text>
  <text x="0" y="232" font-size="10.5" class="dim">The cost is each layer being slightly less expressive, a controlled trade-off.</text>
</svg>
<figcaption>This lever belongs in the initial design, because it changes the shape of the network and not just its size.</figcaption>
</figure>

Both are controlled trade-offs, and the important part is that they belong in the initial design rather than being bolted onto a finished model.

## How the industry does this

**The COCO evaluation standard.** The Microsoft COCO dataset (Lin et al., ECCV 2014) ships with an official evaluation tool, and that tool has shaped how the whole field reports results. It averages AP over ten IoU thresholds from 0.5 to 0.95, which is exactly what the mAP@0.5:0.95 notation cited in every paper means. It also reports AP at IoU 0.5 and at 0.75 separately, and breaks AP out by object size into small, medium and large, because detecting small objects is markedly harder and a single aggregate number hides that.

There is a detail in this tool that often gets overlooked: **per-class AP is the primary result, and mAP is nothing more than their arithmetic mean at the final step**. Put another way, per-class AP is not an extra computation bolted on afterwards; it is what exists first. The aggregate number is what gets derived from it.

**LVIS.** This dataset (Gupta, Dollár, Girshick, CVPR 2019) covers more than a thousand classes with a naturally long-tailed distribution, and was designed largely to expose the rare-class problem. The paper states plainly that modern deep learning methods perform poorly in the low-sample regime, and for that reason LVIS reports AP split by rare, common and frequent class groups rather than as a single total. This is the strongest argument for reporting per-class AP when the data is skewed: it is not a personal preference but the standard of a major benchmark.

**Distillation for detection.** Two works shaped this direction. Chen, Choi, Yu, Han and Chandraker (NeurIPS 2017), *Learning Efficient Object Detection Models with Knowledge Distillation*, address the three detection-specific challenges with three corresponding mechanisms: weighted cross-entropy for class imbalance, a teacher-bounded regression loss for the coordinate part, which penalises the student only when it is worse than the teacher and therefore uses the teacher as an upper bound rather than an absolute target, and adaptation layers for matching intermediate features. Wang, Yuan, Zhang and Feng (CVPR 2019), *Distilling Object Detectors with Fine-grained Feature Imitation*, tackle the background-dominance problem by imitating features only in regions near objects instead of across the whole feature map.

**MLPerf Inference.** Measuring inference speed has been standardised by MLCommons. The benchmark defines four standard load scenarios that reflect the ways real systems receive requests, and splits results into two divisions: Closed requires everyone to use the same model so that hardware comparisons are fair, while Open permits model changes so that algorithmic improvements can be measured too. Submitted results are published with detailed configurations, which means other people can reproduce them.

**MLPerf Tiny.** This is the branch for microcontrollers and very small devices, covering benchmarks such as image classification, person detection, keyword spotting and anomaly detection. It runs in single-stream mode, measures latency and model quality at the same time, because a model that is fast and wrong is worthless, and offers an option to measure energy consumption as well, which is the deciding quantity for anything running on a battery.

## A few takeaways

**Report per-class results when the data is skewed.** An aggregate number over long-tailed data mostly reflects the largest class. Both the COCO evaluation tool and the design of LVIS show that per-class AP is the primary information, so surfacing it is just giving back something that was already there.

**Put deployment constraints into the design phase.** Dropping attention, choosing depthwise separable convolutions and adding a high-resolution detection head are all architectural decisions that follow from the target being the CPU of a device in the field. Attaching that constraint at the start of a project is far cheaper than attaching it at the end.

**Test the format conversion as an independent link.** The path from training framework to device runtime passes through several conversions, and each one can shift the results, through unsupported operators, through rounding differences, or through colour channel order. The right test is to run the same input through both versions and compare the outputs.

**Make the model artifact carry the configuration that produced it.** A weights file does not tell you on its own how many classes it has, what the class names are and in what order, what input size it expects, or how inputs are normalised. Packaging that alongside the weights is what makes the results interpretable later.

**Measure speed in a way other people can reproduce.** If latency is a requirement, it has to be measured with an explicit load scenario and a recorded configuration, in the spirit of the industry benchmarks, rather than by the impression that the app feels smooth.
