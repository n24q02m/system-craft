---
title: "Environmental monitoring: data infrastructure before models"
description: "Storing data that has both a time and a space dimension, forecasting each parameter on its own, and how the field measures forecast error properly."
lang: "en"
order: 5
field: "TS"
topics: ["time series", "forecasting", "geospatial data", "ARIMA", "MASE"]
---

The problem: given air quality and water quality monitoring data, collected at many stations over several years, produce forecasts for the days ahead and raise a warning when something looks likely to cross a safety threshold.

The interesting part of this problem is not where you would expect. Before you get anywhere near a forecasting model, there is an infrastructure problem to solve, and that is where most of the effort goes.

## The system as built

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="Two-dimensional monitoring data passing through a data store and splitting into two forecasting branches">
  <defs><marker id="ts-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box" x="0" y="28" width="156" height="46"/>
  <rect class="box" x="0" y="96" width="156" height="46"/>
  <rect class="box-accent" x="212" y="62" width="180" height="46"/>
  <rect class="box" x="448" y="22" width="192" height="52"/>
  <rect class="box" x="448" y="100" width="192" height="52"/>
  <g class="flow" marker-end="url(#ts-a)">
    <path d="M156 51 H184 V80 H206"/>
    <path d="M156 119 H184 V90 H206"/>
    <path d="M392 78 H418 V44 H442"/>
    <path d="M392 92 H418 V122 H442"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="50">Time dimension</text>
    <text x="10" y="118">Space dimension</text>
    <text x="222" y="82">Data store</text>
    <text x="458" y="42">Deep learning branch</text>
    <text x="458" y="120">Statistical branch</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="66">irregular sampling, gaps</text>
    <text x="10" y="134">coordinates, radius queries</text>
    <text x="222" y="98">time-series and geo indexes</text>
    <text x="458" y="58">one model per parameter</text>
    <text x="458" y="136">auto order search, density clusters</text>
  </g>
  <text x="0" y="180" font-size="10.5" class="dim">Ahead of both branches: a naive forecast to serve as the reference point.</text>
  <text x="0" y="196" font-size="10.5" class="dim">Without a reference, the words good and bad have no meaning.</text>
</svg>
<figcaption>The two dimensions of the data decide how it is stored; the amount of data per series decides which branch to take.</figcaption>
</figure>

### Storage: data with two dimensions

Monitoring data has three characteristics that make it harder to store and query than ordinary tabular data.

**It has a time dimension and a space dimension.** Every measurement is tied to a timestamp and to a geographic coordinate. The common question is not "what was the value at this station yesterday" but "within a few tens of kilometres of this point, what has the weekly average looked like", which is a query that needs both a time index and a geospatial index.

<figure class="diagram">
<svg viewBox="0 0 640 230" role="img" aria-label="A plane of monitoring stations with a radius circle around a query point, next to two kinds of question">
  <text class="lbl dim" x="0" y="20" font-size="9.5">STATION PLANE</text>
  <text class="lbl dim" x="330" y="20" font-size="9.5">TWO KINDS OF QUESTION</text>
  <rect class="box-soft" x="0" y="30" width="296" height="168"/>
  <circle class="node" cx="34" cy="58" r="3"/>
  <circle class="node" cx="70" cy="170" r="3"/>
  <circle class="node" cx="44" cy="112" r="3"/>
  <circle class="node" cx="94" cy="46" r="3"/>
  <circle class="node" cx="232" cy="58" r="3"/>
  <circle class="node" cx="268" cy="104" r="3"/>
  <circle class="node" cx="246" cy="160" r="3"/>
  <circle class="node" cx="206" cy="182" r="3"/>
  <circle class="node" cx="112" cy="182" r="3"/>
  <circle class="node" cx="126" cy="92" r="3"/>
  <circle class="node" cx="176" cy="96" r="3"/>
  <circle class="node" cx="146" cy="152" r="3"/>
  <circle class="node" cx="196" cy="128" r="3"/>
  <circle class="node" cx="118" cy="142" r="3"/>
  <circle class="edge dashed" cx="152" cy="114" r="56"/>
  <line class="edge" x1="96" y1="114" x2="152" y2="114"/>
  <circle class="node-accent" cx="152" cy="114" r="4.5"/>
  <text x="104" y="110" font-size="10" class="dim">radius</text>
  <rect class="box" x="330" y="30" width="306" height="48"/>
  <text x="340" y="50" font-size="11.5">What was the value here yesterday?</text>
  <text x="340" y="66" font-size="10" class="dim">one dimension — a time index is enough</text>
  <rect class="box-accent" x="330" y="94" width="306" height="64"/>
  <text x="340" y="114" font-size="11.5">The weekly average within a radius</text>
  <text x="340" y="130" font-size="10" class="dim">of a few tens of kilometres of this point</text>
  <text x="340" y="144" font-size="10" class="dim">needs a time index and a geospatial index</text>
  <text x="0" y="220" font-size="10.5" class="dim">The same measurement has to be findable along time and across an area.</text>
</svg>
<figcaption>The radius picks out a handful of stations among many; that filtering has to come from a geospatial index rather than a full scan.</figcaption>
</figure>

**It is sparse and irregular.** One station reports hourly, another daily; some go offline for a while and then come back. The assumption that every time step has exactly one value, which underpins most time series models, is not naturally true here. It has to be manufactured through resampling and imputation.

<figure class="diagram">
<svg viewBox="0 0 640 260" role="img" aria-label="Three sites sampling at different cadences, then aligned onto one regular time grid after resampling">
  <defs><marker id="ts-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="16" font-size="9.5">BEFORE — ACTUAL CADENCE</text>
  <line class="axis" x1="60" y1="44" x2="632" y2="44"/>
  <line class="axis" x1="60" y1="68" x2="632" y2="68"/>
  <line class="axis" x1="60" y1="92" x2="632" y2="92"/>
  <line class="axis" x1="60" y1="190" x2="632" y2="190"/>
  <line class="axis" x1="60" y1="210" x2="632" y2="210"/>
  <line class="axis" x1="60" y1="230" x2="632" y2="230"/>
  <circle class="node" cx="80" cy="44" r="2.4"/>
  <circle class="node" cx="120" cy="44" r="2.4"/>
  <circle class="node" cx="160" cy="44" r="2.4"/>
  <circle class="node" cx="200" cy="44" r="2.4"/>
  <circle class="node" cx="240" cy="44" r="2.4"/>
  <circle class="node" cx="280" cy="44" r="2.4"/>
  <circle class="node" cx="320" cy="44" r="2.4"/>
  <circle class="node" cx="360" cy="44" r="2.4"/>
  <circle class="node" cx="400" cy="44" r="2.4"/>
  <circle class="node" cx="440" cy="44" r="2.4"/>
  <circle class="node" cx="480" cy="44" r="2.4"/>
  <circle class="node" cx="520" cy="44" r="2.4"/>
  <circle class="node" cx="560" cy="44" r="2.4"/>
  <circle class="node" cx="600" cy="44" r="2.4"/>
  <circle class="node" cx="96" cy="68" r="2.4"/>
  <circle class="node" cx="212" cy="68" r="2.4"/>
  <circle class="node" cx="328" cy="68" r="2.4"/>
  <circle class="node" cx="444" cy="68" r="2.4"/>
  <circle class="node" cx="560" cy="68" r="2.4"/>
  <circle class="node" cx="80" cy="92" r="2.4"/>
  <circle class="node" cx="124" cy="92" r="2.4"/>
  <circle class="node" cx="168" cy="92" r="2.4"/>
  <circle class="node" cx="212" cy="92" r="2.4"/>
  <circle class="node" cx="256" cy="92" r="2.4"/>
  <circle class="node" cx="428" cy="92" r="2.4"/>
  <circle class="node" cx="472" cy="92" r="2.4"/>
  <circle class="node" cx="516" cy="92" r="2.4"/>
  <circle class="node" cx="560" cy="92" r="2.4"/>
  <circle class="node" cx="604" cy="92" r="2.4"/>
  <line class="grid" x1="88" y1="182" x2="88" y2="240"/>
  <line class="grid" x1="152" y1="182" x2="152" y2="240"/>
  <line class="grid" x1="216" y1="182" x2="216" y2="240"/>
  <line class="grid" x1="280" y1="182" x2="280" y2="240"/>
  <line class="grid" x1="344" y1="182" x2="344" y2="240"/>
  <line class="grid" x1="408" y1="182" x2="408" y2="240"/>
  <line class="grid" x1="472" y1="182" x2="472" y2="240"/>
  <line class="grid" x1="536" y1="182" x2="536" y2="240"/>
  <line class="grid" x1="600" y1="182" x2="600" y2="240"/>
  <text x="0" y="48" font-size="10" class="dim">Site A</text>
  <text x="0" y="72" font-size="10" class="dim">Site B</text>
  <text x="0" y="96" font-size="10" class="dim">Site C</text>
  <text x="307" y="88" font-size="10" class="dim">offline</text>
  <text x="60" y="116" font-size="10" class="dim">A reports often, B rarely, C goes offline then returns</text>
  <path class="flow" marker-end="url(#ts-a2)" d="M380 130 V156"/>
  <text x="392" y="148" font-size="10.5" class="dim">resample and impute</text>
  <text class="lbl dim" x="0" y="172" font-size="9.5">AFTER — REGULAR TIME GRID</text>
  <circle class="node" cx="88" cy="190" r="3"/>
  <circle class="node" cx="152" cy="190" r="3"/>
  <circle class="node" cx="216" cy="190" r="3"/>
  <circle class="node" cx="280" cy="190" r="3"/>
  <circle class="node" cx="344" cy="190" r="3"/>
  <circle class="node" cx="408" cy="190" r="3"/>
  <circle class="node" cx="472" cy="190" r="3"/>
  <circle class="node" cx="536" cy="190" r="3"/>
  <circle class="node" cx="600" cy="190" r="3"/>
  <circle class="node" cx="88" cy="210" r="3"/>
  <circle class="node" cx="216" cy="210" r="3"/>
  <circle class="node" cx="344" cy="210" r="3"/>
  <circle class="node" cx="472" cy="210" r="3"/>
  <circle class="node" cx="536" cy="210" r="3"/>
  <circle class="node-open" cx="152" cy="210" r="3"/>
  <circle class="node-open" cx="280" cy="210" r="3"/>
  <circle class="node-open" cx="408" cy="210" r="3"/>
  <circle class="node-open" cx="600" cy="210" r="3"/>
  <circle class="node" cx="88" cy="230" r="3"/>
  <circle class="node" cx="152" cy="230" r="3"/>
  <circle class="node" cx="216" cy="230" r="3"/>
  <circle class="node" cx="472" cy="230" r="3"/>
  <circle class="node" cx="536" cy="230" r="3"/>
  <circle class="node" cx="600" cy="230" r="3"/>
  <circle class="node-open" cx="280" cy="230" r="3"/>
  <circle class="node-open" cx="344" cy="230" r="3"/>
  <circle class="node-open" cx="408" cy="230" r="3"/>
  <text x="0" y="194" font-size="10" class="dim">Site A</text>
  <text x="0" y="214" font-size="10" class="dim">Site B</text>
  <text x="0" y="234" font-size="10" class="dim">Site C</text>
  <circle class="node" cx="64" cy="248" r="3"/>
  <text x="74" y="252" font-size="10" class="dim">real measurement</text>
  <circle class="node-open" cx="170" cy="248" r="3"/>
  <text x="180" y="252" font-size="10" class="dim">imputed value</text>
  <text x="300" y="252" font-size="10" class="dim">imputation is a modelling decision, not a cleanup step</text>
</svg>
<figcaption>The regular grid is manufactured during processing rather than found in the data; the open points are values we chose how to produce.</figcaption>
</figure>

**Each parameter is its own series.** Ozone concentration and the concentration of a trace metal differ in magnitude by a factor of thousands, have different cycles, and are produced by different physical mechanisms.

The storage answer is a document database that ships with the two things this problem needs: **time series collections** (optimised for append-only data on a time axis, with good compression within time buckets) and **geospatial indexes** (queries by radius, by polygon, by distance). Those two features address exactly the two dimensions of the problem without having to build them.

### The data pipeline

The sources are public monitoring datasets that follow environmental agency standards: air quality tables with state code, county code, site code, coordinates, parameter name, mean value and air quality index; water quality tables with organisation identifier, monitoring location identifier, characteristic name and result value.

The processing steps: normalise parameter names, resample onto a regular time grid, impute missing values, normalise units, then load into the database under the designed schema. Imputation is a modelling decision, not a harmless cleanup step. How you fill the gaps feeds directly into what the model learns.

### Air forecasting: a recurrent network per parameter

Rather than one model covering every parameter, the system trains **a separate model for each parameter**. The reason is the one given above: parameters differ in magnitude, in cycle and in mechanism, so pooling them usually does worse.

The architecture is a multi-layer LSTM with an attention mechanism, dropout and batch normalisation, with early stopping on a validation set. The output is a forecast over a window of the next few days.

The individual model outputs are combined into a **composite health risk index**: each parameter gets a weight reflecting how harmful it is, is converted onto a common scale, and the results are summed and mapped onto warning levels. The index is also decomposed by affected organ system, respiratory, cardiovascular and neurological, so the warning means something to whoever reads it.

### Water forecasting: classical statistics and spatial clustering

The water quality branch goes in a completely different direction: no deep learning.

**Spatial clustering** with a density-based clustering algorithm. What makes this algorithm a good fit for geographic data is that it needs no number of clusters up front, it finds clusters of arbitrary shape, and it marks points that belong to no cluster as noise, which suits monitoring stations scattered unevenly.

<figure class="diagram">
<svg viewBox="0 0 640 240" role="img" aria-label="Stations on a plane forming three dense regions of different shapes, with a few isolated points marked as noise">
  <text class="lbl dim" x="0" y="20" font-size="9.5">MONITORING STATIONS ON A PLANE</text>
  <text class="lbl dim" x="364" y="20" font-size="9.5">THREE PROPERTIES</text>
  <rect class="box-soft" x="0" y="28" width="340" height="190"/>
  <circle class="node" cx="145" cy="114" r="3"/>
  <circle class="node" cx="136" cy="129" r="3"/>
  <circle class="node" cx="122" cy="141" r="3"/>
  <circle class="node" cx="105" cy="147" r="3"/>
  <circle class="node" cx="87" cy="147" r="3"/>
  <circle class="node" cx="70" cy="141" r="3"/>
  <circle class="node" cx="56" cy="129" r="3"/>
  <circle class="node" cx="47" cy="114" r="3"/>
  <circle class="node" cx="129" cy="119" r="3"/>
  <circle class="node" cx="113" cy="132" r="3"/>
  <circle class="node" cx="92" cy="136" r="3"/>
  <circle class="node" cx="73" cy="129" r="3"/>
  <circle class="node" cx="60" cy="113" r="3"/>
  <circle class="node" cx="176" cy="52" r="3"/>
  <circle class="node" cx="190" cy="60" r="3"/>
  <circle class="node" cx="204" cy="68" r="3"/>
  <circle class="node" cx="218" cy="76" r="3"/>
  <circle class="node" cx="232" cy="84" r="3"/>
  <circle class="node" cx="246" cy="92" r="3"/>
  <circle class="node" cx="170" cy="62" r="3"/>
  <circle class="node" cx="184" cy="70" r="3"/>
  <circle class="node" cx="198" cy="78" r="3"/>
  <circle class="node" cx="212" cy="86" r="3"/>
  <circle class="node" cx="226" cy="94" r="3"/>
  <circle class="node" cx="198" cy="148" r="3"/>
  <circle class="node" cx="212" cy="146" r="3"/>
  <circle class="node" cx="226" cy="149" r="3"/>
  <circle class="node" cx="240" cy="156" r="3"/>
  <circle class="node" cx="249" cy="168" r="3"/>
  <circle class="node" cx="250" cy="181" r="3"/>
  <circle class="node" cx="241" cy="191" r="3"/>
  <circle class="node" cx="227" cy="195" r="3"/>
  <circle class="node" cx="213" cy="190" r="3"/>
  <circle class="node" cx="222" cy="166" r="3"/>
  <circle class="node-open" cx="30" cy="58" r="3.2"/>
  <circle class="node-open" cx="156" cy="190" r="3.2"/>
  <circle class="node-open" cx="300" cy="120" r="3.2"/>
  <circle class="node-open" cx="292" cy="44" r="3.2"/>
  <circle class="node-open" cx="78" cy="202" r="3.2"/>
  <circle class="node-open" cx="306" cy="196" r="3.2"/>
  <text x="38" y="54" font-size="10" class="dim">noise</text>
  <rect class="box" x="364" y="28" width="272" height="52"/>
  <text x="374" y="48" font-size="11.5">No cluster count needed</text>
  <text x="374" y="64" font-size="10" class="dim">the algorithm decides</text>
  <rect class="box" x="364" y="94" width="272" height="52"/>
  <text x="374" y="114" font-size="11.5">Clusters of arbitrary shape</text>
  <text x="374" y="130" font-size="10" class="dim">no assumption of round blobs</text>
  <rect class="box" x="364" y="160" width="272" height="52"/>
  <text x="374" y="180" font-size="11.5">Outliers marked as noise</text>
  <text x="374" y="196" font-size="10" class="dim">not forced into any cluster</text>
  <text x="0" y="234" font-size="10.5" class="dim">A cluster here is a dense region of stations, not a circle around a centre.</text>
</svg>
<figcaption>The three dense regions have quite different shapes; six isolated points belong to none of them and are left out rather than forced into the nearest cluster.</figcaption>
</figure>

**Forecasting with ARIMA and automatic order selection.** ARIMA is a statistical model combining three components: autoregression, where the current value depends linearly on previous values; differencing, taking differences to remove trend and bring the series to a stationary form; and a moving average term, a dependence on previous forecast errors. Choosing those three orders is usually done by hand from autocorrelation plots; the library used here searches a parameter grid automatically and selects by information criterion.

Beyond forecasting, this branch also computes a **threshold exceedance rate** for each characteristic, meaning what fraction of measurements fall outside the safe range, and raises a warning when the forecast shows a sustained trend past the threshold.

## Background

### Why time series differ from other machine learning problems

The fundamental difference: **the most recent value is already a very good forecast.** Tomorrow's temperature is close to today's. With seasonal data, the value from the same point in the previous season is better still.

These two methods, the naive forecast and the seasonal naive forecast, have no parameters to learn and run instantly. They are a mandatory starting point, not because they are good, but because without them the words "good" and "bad" have no meaning for any number that comes afterwards.

<figure class="diagram">
<svg viewBox="0 0 640 220" role="img" aria-label="A seasonal series with two naive forecast lines starting from the end of training">
  <path class="axis" d="M24 30 V170 H620"/>
  <line class="axis dashed" x1="414" y1="30" x2="414" y2="176"/>
  <text class="lbl dim" x="194" y="24" font-size="9.5">TRAINING</text>
  <text class="lbl dim" x="490" y="24" font-size="9.5">FORECAST</text>
  <path class="curve" d="M30 134 C47.5 134 60.5 66 78 66 C95.5 66 108.5 134 126 134 C143.5 134 156.5 66 174 66 C191.5 66 204.5 134 222 134 C239.5 134 252.5 66 270 66 C287.5 66 300.5 134 318 134 C335.5 134 348.5 66 366 66 C383.5 66 396.5 134 414 134"/>
  <path class="curve-warn dashed" d="M414 134 H606"/>
  <path class="curve-accent dashed" d="M414 134 C431.5 134 444.5 66 462 66 C479.5 66 492.5 134 510 134 C527.5 134 540.5 66 558 66 C575.5 66 588.5 134 606 134"/>
  <line class="curve-warn dashed" x1="0" y1="192" x2="22" y2="192"/>
  <text x="28" y="196" font-size="10.5" class="dim">naive — carry the last value forward</text>
  <line class="curve-accent dashed" x1="0" y1="208" x2="22" y2="208"/>
  <text x="28" y="212" font-size="10.5" class="dim">seasonal naive — repeat the previous season</text>
  <text x="330" y="196" font-size="10.5" class="dim">No parameters to fit, runs instantly.</text>
  <text x="330" y="212" font-size="10.5" class="dim">Without this reference, nothing is good or bad.</text>
</svg>
<figcaption>The flat line is the entire content of the naive forecast; a complex model has to beat it before it is worth discussing.</figcaption>
</figure>

### Stationarity

Most statistical time series models assume the series is **stationary**: statistical properties such as the mean and the variance do not change over time. Real data rarely is. It has long-run trends and seasonal cycles. The differencing step in ARIMA exists to remove trend, and the seasonal variants exist to remove the cycle.

<figure class="diagram">
<svg viewBox="0 0 640 268" role="img" aria-label="An original series whose mean drifts upward, and the differenced series oscillating around a constant level">
  <defs><marker id="ts-a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="16" font-size="9.5">ORIGINAL SERIES — TREND AND SEASONALITY</text>
  <path class="axis" d="M24 26 V112 H620"/>
  <path class="curve" d="M30 108 C47.5 108 60.5 80.3 78 80.3 C95.5 80.3 108.5 100.7 126 100.7 C143.5 100.7 156.5 73 174 73 C191.5 73 204.5 93.3 222 93.3 C239.5 93.3 252.5 65.7 270 65.7 C287.5 65.7 300.5 86 318 86 C335.5 86 348.5 58.3 366 58.3 C383.5 58.3 396.5 78.7 414 78.7 C431.5 78.7 444.5 51 462 51 C479.5 51 492.5 71.3 510 71.3 C527.5 71.3 540.5 43.7 558 43.7 C575.5 43.7 588.5 64 606 64"/>
  <line class="curve-accent dashed" x1="30" y1="96" x2="606" y2="52"/>
  <line class="curve-accent dashed" x1="0" y1="128" x2="22" y2="128"/>
  <text x="28" y="132" font-size="10" class="dim">the rolling mean drifts over time — not stationary</text>
  <path class="flow" marker-end="url(#ts-a3)" d="M600 122 V152"/>
  <text x="470" y="141" font-size="10.5" class="dim">one differencing step</text>
  <text class="lbl dim" x="0" y="166" font-size="9.5">AFTER ONE DIFFERENCING STEP</text>
  <path class="axis" d="M24 174 V242 H620"/>
  <path class="curve" d="M30 226 C47.5 226 60.5 190 78 190 C95.5 190 108.5 228 126 228 C143.5 228 156.5 188 174 188 C191.5 188 204.5 224 222 224 C239.5 224 252.5 192 270 192 C287.5 192 300.5 227 318 227 C335.5 227 348.5 189 366 189 C383.5 189 396.5 225 414 225 C431.5 225 444.5 191 462 191 C479.5 191 492.5 226 510 226 C527.5 226 540.5 190 558 190 C575.5 190 588.5 224 606 224"/>
  <line class="curve-accent dashed" x1="30" y1="208" x2="606" y2="208"/>
  <line class="curve-accent dashed" x1="0" y1="256" x2="22" y2="256"/>
  <text x="28" y="260" font-size="10" class="dim">the rolling mean is flat — the series is stationary</text>
</svg>
<figcaption>Differencing does not make the data better; it puts the data into the shape a statistical model assumes it already has.</figcaption>
</figure>

Neural networks do not require the assumption, but in exchange they need far more data to learn on their own the structure that a statistical model is simply told.

### When deep learning has an edge and when it does not

Deep models need **many observations per series** to beat statistical methods. When a series has only a few hundred points, the network's parameter count far exceeds the information in the data, and what it mostly learns is noise.

<figure class="diagram">
<svg viewBox="0 0 640 226" role="img" aria-label="Two forecast quality curves crossing as the number of observations per series increases">
  <text class="lbl dim" x="0" y="18" font-size="9.5">FORECAST QUALITY</text>
  <rect class="area" x="120" y="26" width="120" height="154"/>
  <text class="lbl dim" x="124" y="40" font-size="9.5">THIS PROBLEM</text>
  <path class="axis" d="M40 26 V180 H610"/>
  <line class="axis dashed" x1="305" y1="26" x2="305" y2="186"/>
  <path class="curve" d="M60 140 L90 128 L120 118.4 L150 110.6 L185 103.4 L220 97.8 L260 92.9 L305 88.8 L350 85.8 L400 83.5 L450 81.8 L500 80.7 L550 79.9 L600 79.3"/>
  <path class="curve-accent" d="M60 170 L90 153.6 L120 139.7 L150 127.7 L185 116 L220 106.2 L260 97.1 L305 88.8 L350 82.3 L400 76.7 L450 72.4 L500 69.1 L550 66.5 L600 64.5"/>
  <circle class="node-accent" cx="305" cy="88.8" r="4"/>
  <text x="312" y="44" font-size="10.5" class="dim">crossing point</text>
  <text x="124" y="166" font-size="10" class="dim">a few hundred points per series — statistics wins here</text>
  <text class="num" x="44" y="194">few</text>
  <text class="num" x="586" y="194">many</text>
  <text class="lbl dim" x="240" y="194" font-size="9.5">OBSERVATIONS PER SERIES</text>
  <line class="curve" x1="0" y1="210" x2="22" y2="210"/>
  <text x="28" y="214" font-size="10.5" class="dim">classical statistics</text>
  <line class="curve-accent" x1="180" y1="210" x2="202" y2="210"/>
  <text x="208" y="214" font-size="10.5" class="dim">deep learning</text>
  <text x="320" y="214" font-size="10.5" class="dim">Where the curves cross depends on data per series.</text>
</svg>
<figcaption>The crossing point, rather than the architecture itself, is what decides which branch suits a given dataset.</figcaption>
</figure>

Deep learning gains its advantage when there are many related series to learn a shared representation from, when there are complex exogenous variables, or when the relationships are clearly non-linear. A moderately sized set of monitoring stations is not obviously a good case for it.

## How the industry does this

### Choosing an error measure

The natural reflex when reporting forecast error is mean absolute percentage error. It is intuitive and everyone understands it. But it has a serious failure mode on exactly this kind of data: **it divides by the actual value**, and many environmental parameters sit very close to zero most of the time. That is the normal state, not corrupted data. When the denominator approaches zero, the ratio blows up.

<figure class="diagram">
<svg viewBox="0 0 640 244" role="img" aria-label="A percentage error curve running to infinity as the actual value approaches zero, while the baseline-scaled measure stays flat">
  <defs><marker id="ts-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="area-warn" x="60" y="28" width="64" height="172"/>
  <path class="axis" d="M60 24 V200 H436"/>
  <line class="axis dashed" x1="60" y1="140" x2="430" y2="140"/>
  <text class="num" x="48" y="144">1</text>
  <text class="lbl dim" x="0" y="18" font-size="9.5">METRIC VALUE</text>
  <path class="curve-warn" d="M68 28 L70 52.9 L72 69.6 L75 86.2 L78 97.3 L82 107.4 L86 114.3 L92 121.5 L100 127.8 L110 132.8 L124 137.1 L140 140.2 L160 142.7 L185 144.7 L215 146.3 L250 147.5 L290 148.4 L340 149.1 L430 150"/>
  <path class="curve-accent" d="M62 160 H430"/>
  <path class="flow" marker-end="url(#ts-a4)" d="M146 48 H110"/>
  <text x="150" y="52" font-size="11.5">Actual values near zero are the normal state</text>
  <text x="150" y="68" font-size="10" class="dim">for environmental data, not corrupted data</text>
  <text x="200" y="134" font-size="10" class="dim">above one: worse than the naive forecast</text>
  <text x="200" y="176" font-size="10" class="dim">below one: better than the naive forecast</text>
  <line class="edge" x1="432" y1="150" x2="440" y2="144"/>
  <line class="edge" x1="432" y1="160" x2="440" y2="176"/>
  <text x="444" y="140" font-size="11.5">MAPE</text>
  <text x="444" y="154" font-size="10" class="dim">divides by the actual value</text>
  <text x="444" y="178" font-size="11.5">MASE</text>
  <text x="444" y="192" font-size="10" class="dim">divides by the naive error</text>
  <text class="lbl dim" x="360" y="216" font-size="9.5">ACTUAL VALUE</text>
  <text x="0" y="238" font-size="10.5" class="dim">In the danger zone the measure still returns a number. It raises no error.</text>
</svg>
<figcaption>The shaded band is where most environmental data actually lives, and it is exactly where a percentage measure stops meaning anything.</figcaption>
</figure>

The standard work on this problem, published in the field's forecasting journal, shows that even the "symmetric" variant of that measure does not rescue it: it still divides by a quantity that can be very small, and despite having the word "absolute" in its name, it can still take negative values. The paper illustrates the point with real series containing zero or negative values, where the measure returns infinity or is simply undefined.

The proposed alternative is **MASE**, the mean absolute scaled error. Instead of dividing by the actual value, it divides the error by the mean error of the naive method computed on the training set. Three properties make it a good fit: it is scale-independent, so it can be compared across parameters that live on different scales; it is never undefined unless the series is constant; and it comes with a natural interpretive reference point, where below one means better than the naive forecast and above one means worse.

### Benchmarks in the field

The field's large-scale forecasting competitions set the practical standard. One used hundreds of thousands of series drawn from many different domains and dozens of competing methods, evaluated with baseline-scaled measures and requiring prediction intervals rather than just point forecasts. Another used hierarchically structured retail sales data with tens of thousands of series, and reported improvement over the best benchmark rather than raw error.

The field's standard textbook, written by the same co-author of MASE and published free of charge, adds two points: compare against the naive method before concluding that a complex model is worth anything, and evaluate with genuine forecasts on a test set, because a model that fits the training data very well is no guarantee of forecasting well.

## A few takeaways

**A baseline is a frame of reference, not a ritual.** With time series the baseline is surprisingly strong, so skipping this step makes it easy to celebrate a result that is in fact worse than doing nothing.

**The metric has to match the character of the data.** An unsuitable metric still produces a number, and that is precisely the danger: it raises no error, it just hands the reader something meaningless to believe.

**Adding synthetic data is not automatically a gain.** If the generating process does not reflect the mechanism that produced the real data, the model learns the generator's distribution. The cheap check is to always keep a branch trained only on real data and compare the two on the same real test set.

**A composite index has to state its assumptions.** The weight on each parameter and the warning thresholds are domain judgements, not technical choices. Writing them down with sources is what makes them checkable by someone else.

**Data infrastructure is the longest-lived investment.** Models get replaced; the storage schema, the indexes and the cleaning pipeline stay around far longer.
