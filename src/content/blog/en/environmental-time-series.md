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

**It is sparse and irregular.** One station reports hourly, another daily; some go offline for a while and then come back. The assumption that every time step has exactly one value, which underpins most time series models, is not naturally true here. It has to be manufactured through resampling and imputation.

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

**Forecasting with ARIMA and automatic order selection.** ARIMA is a statistical model combining three components: autoregression, where the current value depends linearly on previous values; differencing, taking differences to remove trend and bring the series to a stationary form; and a moving average term, a dependence on previous forecast errors. Choosing those three orders is usually done by hand from autocorrelation plots; the library used here searches a parameter grid automatically and selects by information criterion.

Beyond forecasting, this branch also computes a **threshold exceedance rate** for each characteristic, meaning what fraction of measurements fall outside the safe range, and raises a warning when the forecast shows a sustained trend past the threshold.

## Background

### Why time series differ from other machine learning problems

The fundamental difference: **the most recent value is already a very good forecast.** Tomorrow's temperature is close to today's. With seasonal data, the value from the same point in the previous season is better still.

These two methods, the naive forecast and the seasonal naive forecast, have no parameters to learn and run instantly. They are a mandatory starting point, not because they are good, but because without them the words "good" and "bad" have no meaning for any number that comes afterwards.

### Stationarity

Most statistical time series models assume the series is **stationary**: statistical properties such as the mean and the variance do not change over time. Real data rarely is. It has long-run trends and seasonal cycles. The differencing step in ARIMA exists to remove trend, and the seasonal variants exist to remove the cycle.

Neural networks do not require the assumption, but in exchange they need far more data to learn on their own the structure that a statistical model is simply told.

### When deep learning has an edge and when it does not

Deep models need **many observations per series** to beat statistical methods. When a series has only a few hundred points, the network's parameter count far exceeds the information in the data, and what it mostly learns is noise.

Deep learning gains its advantage when there are many related series to learn a shared representation from, when there are complex exogenous variables, or when the relationships are clearly non-linear. A moderately sized set of monitoring stations is not obviously a good case for it.

## How the industry does this

### Choosing an error measure

The natural reflex when reporting forecast error is mean absolute percentage error. It is intuitive and everyone understands it. But it has a serious failure mode on exactly this kind of data: **it divides by the actual value**, and many environmental parameters sit very close to zero most of the time. That is the normal state, not corrupted data. When the denominator approaches zero, the ratio blows up.

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
