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

There is also a step that generates object-free background images through inpainting: take a real frame, erase the vehicles, and let the algorithm fill the hole back in with plausible background. These serve as negative examples, teaching the model that an empty stretch of road has nothing to report.

### Two-tier augmentation

Data augmentation is split into two tiers, and the boundary between them is a deliberate design decision.

The offline tier runs before training, through a dedicated image transformation library, and writes its results to disk as images. The transforms cover horizontal flips; shifts, rotations and scaling; colour and brightness changes; blur; added noise. The most important group is the weather simulations: rain, fog, snow, cast shadows, sun flare. That group maps directly onto the bad-conditions requirement, and it is also the most expensive to compute.

The on-the-fly tier, meaning the augmentation built into the training framework, is almost entirely switched off. What remains is mosaic, which stitches four images into one so the model sees several contexts and several scales in a single sample, along with random erasing of an image region.

The split comes out of a specific trade-off. Generating variants during training is the default in most frameworks because the model sees a different variant every epoch, so it buys more regularisation for the same storage. But the weather simulations are expensive, and paying that cost every epoch is waste; computing them once and caching them is far cheaper.

The risk of running both tiers at once is equally specific: distortions compound. An image already baked with rain and reduced brightness, if it then picks up a colour shift and a blur at training time, can drift away from any frame a real camera would ever record. Picking one tier as primary and writing down why is how you avoid that.

### The student-teacher architecture

The model size constraint is handled with knowledge distillation, with two models playing two roles.

**The teacher** is a large object detector from the YOLO family, fine-tuned from weights pre-trained on a general-purpose image set. Its only job is to be a source of supervisory signal; it is never deployed.

**The student** is a custom architecture defined through a config file, with three changes relative to the stock design:

- Every standard convolution is replaced with a depthwise separable convolution, or a Ghost variant. This is where most of the parameter reduction comes from.
- A detection head is added at a higher resolution, giving four heads instead of three. Vehicles far down the frame in a traffic camera view occupy very few pixels, and a higher-resolution head gives the model a chance to catch them.
- No attention modules at all. This is a deliberate constraint: attention blocks add latency and tend to be poorly supported on mobile runtimes, so they were ruled out at design time.

Distillation keeps the teacher frozen. The loss has two parts: the ordinary detection term computed against ground truth, plus a distillation term based on the KL divergence between the student's output distribution and the teacher's. That second part has two knobs, temperature, which softens the distribution so low-probability classes still contribute signal, and a mixing coefficient, which decides how much the student listens to the ground truth against how much it listens to the teacher.

### Inference and preprocessing

The system supports two inference modes. The standard mode pushes the whole frame through the model once. The tiled mode splits a large image into overlapping cells, runs the model on each cell, and merges the results. This costs several times the compute, but it makes small objects large relative to the model's input, so it catches distant vehicles that the standard mode misses. The overlap exists so that a vehicle straddling the boundary between two cells does not get cut in half.

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

### Knowledge distillation and the dark knowledge intuition

Knowledge distillation trains a small model to match not only the ground truth labels but also the output distribution of a larger model that has already finished training.

The intuition is about how much information each signal carries. A hard label says only "this is a motorcycle", one bit about the correct class and nothing more. The teacher's output distribution says "this is a motorcycle, somewhat similar to a bicycle, and almost certainly not a bus". That relational structure between classes, sometimes called dark knowledge, is what hard labels do not carry, and it is why a student learns faster from a teacher than from labels alone.

### Why distillation for detection differs from distillation for classification

The technique was invented for image classification and does not transfer straight across to detection, for three reasons.

First, most of the area in a frame is background. Force the student to imitate the teacher across the entire feature map and almost all of the learned signal will be about background, which nobody cares about.

Second, detection has a coordinate regression component, not just classification. Forcing the student to match the teacher exactly on coordinates can backfire when the teacher itself is off.

Third, the imbalance between background and objects is far more severe than ordinary class imbalance in classification, so the loss needs a mechanism to compensate.

### The trade-off between accuracy and size

There are two main levers for shrinking a model. Depthwise separable convolution splits a standard convolution into two steps, a per-channel filter followed by a channel mixing step through a 1x1 convolution, cutting the number of multiplications and parameters by a large factor at the cost of each layer being slightly less expressive. Quantisation represents weights as low-width integers rather than floats, reducing size and speeding things up on hardware with integer support, at the cost of some numerical resolution.

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
