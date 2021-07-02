# Model description

The inference model is implemented for a patched version of BEAST v2.6.4-prerelease.

```xml
<beast namespace="beast.math.distributions:beast.core:beast.evolution.operators:beast.evolution.alignment:beast.evolution.substitutionmodel" version="2.6">
```

The data is extracted from the corresponding datasets using Lexedata
v1.0.0. For each core concept, we encode the presence or absence of each cognate
class connected to that concept in the language as a binary character. Because
we cannot observe cognate classes that don't appear in our data at all, we
correct the model for this ascertainment bias.

```xml
<data>...</data>
<userDataType id="binary" spec="beast.evolution.datatype.Binary" />
<plate var="concept" range="{partitions}">
  <data id="data:$(concept)" userDataType="@binary" spec="FilteredAlignment" ascertained="true" data="@concept:$(concept)" excludeto="1" filter="::" />
</plate>
```

## Likelihood

The likelihood of the MCMC uses a generalized binary substitution model on a
tree where node height represents time depth. We use one partition per concept.

```xml
<distribution id="likelihood" spec="util.CompoundDistribution">
  <plate var="concept" range="{partitions}">
    <distribution id="likelihood:$(concept)" spec="beast.evolution.likelihood.TreeLikelihood" tree="@tree" siteModel="@SiteModel:$(concept)" data="@data:$(concept)" branchRateModel="@StrictClock" />
  </plate>
</distribution>
```

The baseline for our clock model is a strict clock.

```xml
<branchRateModel id="StrictClock" spec="beast.evolution.branchratemodel.StrictClockModel" clock.rate="@clockrate" />
```

We assume a simple generalized binary continuous-time Markov chain substitution
model for each separate character. The substitution rates from presence to
absence and vice versa are derived from the equilibrium frequencies of present
and absent states.

```xml
<substModel id="CTMC" spec="GeneralSubstitutionModel">
   <parameter id="rates" spec="parameter.RealParameter" dimension="2" estimate="false" lower="0.0" name="rates">1.0 1.0</parameter>
   <frequencies id="estimatedFreqs" spec="Frequencies" frequencies="@freqParameter" />
</substModel>

```

It is well-known that rates of lexical replacement differ greatly between
different concepts. We therefore include a model of rate variation in our model.
For computational efficiency, it is vastly more efficient to integrate out
per-site rate variation than to sample rate variation explicitly, but this is
not doable per-partition. Instead, we define a separate speed of change for
every concept explicitly.

```xml
<plate var="concept" range="{partitions}">
  <siteModel id="SiteModel:$(concept)" spec="beast.evolution.sitemodel.SiteModel" mutationRate="@speed:$(concept)" proportionInvariant="0.0" substModel="@CTMC" />
</plate>
```

## Priors

```xml
<distribution id="prior" spec="util.CompoundDistribution">
```


For the tree prior, we take a variant of the fossilized birth death (FBD) tree
prior with sampled ancestors (SA). The basic FBD prior has the following
parameters:

 - a birth rate `λ` that describes how frequently a taxon splits into two descendants
 - a death rate `μ` which measures how quickly taxa go extinct
 - a sampling rate `φ` for the frequency of a taxon leaving traces that can be observed today
 
Due to the age of our samples compared with the age of any known lanugage family
we can be sure that none of our samples *is* proto-Arawakan, and condition on
the fact that the first event in the tree is a binary split, not a sampling
event (or an extinction, in which case we would observe no descendants). We can
therefore condition the likelihood on the root, instead of specifying a starting
time for the diversification process.

```xml
<distribution id="BirthDeath" spec="beast.evolution.speciation.BirthDeathSkylineModel" tree="@tree"
conditionOnRoot="true">
```

This parameterization is difficult to estimate, so we use the parameterization
usual in phylogenetics, where the same set of parameter values is expressed by a
net diversification rate `λ-μ`, a turnover parameter `(μ+φ)/(λ+μ+φ)` and a
sampling proportion `φ/(μ+φ)`.
```xml
<netDiversification idref="netDiversificationRate" />
<turnOver idref="turnOver" />
<samplingProportion idref="SamplingProportion" />
```
> I would like to set the older sampling proportion to 0.0, but that breaks
> the model, so maybe it should be about 1/10000, because there were
> presumably thousands of languages that died out before Christians and
> linguists started collecting languages, and only a handful have left
> writing that would give us enough data for word lists.

> It is not clear to
> us yet how to set different priors for the two different time ranges, but that
> would probably be handy in the future.
             
The sampling proportion represents, in some approximation, the probability that
a language was studied before it had a ‘chance’ to die out. The removal
probability, on the other hand, represents the fact that the sampling process
has a causal connection to the language dying out. (This concept comes from
epidemiological phylogenetics, where a patient's pathogens are not just
sequenced, but in the process the patient is also isolated, thus preventing the
pathogens from reproducing further.) In field linguistics, the impending loss of
a language may be an incentive for linguists to collaborate with the last
remaining speakers to document the language, so there is a causal connection,
but in general, language documentation has a potentially strengthening effect on
language communities, so we pin the removal probability to $0.0$.

```xml
<parameter name="removalProbability" id="removalProbability">0.0</parameter>
```

Our data does not contain all extant languages, so we need to also specify the
sampling probabilty $\rho$ of extant languages. There are XXX extant Arawak
languages listed in Glottolog, and our sample contains 39 tips of which XXX are
extant, so $\rho = 0.51$.

```xml
<parameter name="rho">0.5131578947368421</parameter>
```

The variant of the FBD we use, the FBD-Skyline model, assumes that those tree
parameters can change at given points in time (in our case, time measured
backwards from the tips, not forwards from the root). The arrivial of Christian
missionaries in the region ca. 500 years ago marks a change in the ‘linguistic
ecology’ of the region. In particular, attestations of languages before that
time are nearly impossible to come by, while afterwards the chance that word
lists are collected and survive until today is much larger.

```xml
<reverseTimeArrays spec="beast.core.parameter.BooleanParameter">true true true true true</reverseTimeArrays>
<parameter name="samplingRateChangeTimes" id="SamplingChangeTime">0. 500.</parameter>
</distribution>
```

We know very little about the diversification speed of languages, but we can
roughly estimate its order of magnitude. The mean number of languages in a
language family, according to Glottolog, is about 20. Only 5\% of language
families have more than 55 languages in them. Common wisdom has it that the time
depth of the comparative method, which is used to assess the relatedness of
languages, is about 8000 years (but highly dependent on data availability). (In
principle, we would have to exclude the language family studied here from that
count, so as to not include their number of languages twice in the posterior
distribution.)

A language family that started from 1 language 8000 years ago and reached 20
languages today would have doubled with an average rate of $\log_2 20 / 8000 =
0.00054$. years. To diversify into 55 languages in about 3000 years, the
diversification rate would be $\log_2 55 / 4000 = 0.00145$, or about a factor
$e$ higher. This gives us a way to specify a lognormal prior:

```xml
<prior spec="Prior" id="BirthRatePrior" name="distribution" x="@netDiversificationRate">
<distr id="LogNormal.BirthRate" spec="beast.math.distributions.LogNormalDistributionModel">
```

The mean of the distribution in log space is $M=\ln 0.00054=-7.52$.

```xml
<M id="LogNormalMean.BirthRate" spec="parameter.RealParameter" estimate="false">-7.52349519971536</M>
```

The 95\% mark corresponds to roughly the $3\sigma$ interval around the mean, and
a factor of $e$ translates into a $\pm 1$ in log space, so $S=1/3$.

```xml
<S id="LogNormalStd.BirthRate" spec="parameter.RealParameter" estimate="false">0.3333333333333333333</S>
</distr>
</prior>
```

Death rates/turnover are much more difficult to estimate. We do not know much,
but we do know some lanugages are extinct. In the expanding lanugage families
that are generally studied, it seems like the majority are not extinct. And we
vaguely see death rates around 0.2~0.5 inferred in other language phylogenies –
these numbers are rarely reported, so it requires good supplementary material.

On the other hand, language shift is a persistent phenomenon around the world
and has been for a long time [@???]. This suggests that we don't actually know
much about the distribution of death rates and should use a uniform prior
between 0 and 1.

```xml
<prior spec="Prior" id="DeathRatePrior" name="distribution" x="@turnOver">
  <distr spec="Uniform" lower="0" upper="1" />
</prior>
```

The strict clock is governed by a clock rate parameter. In BEAST, substitution
models are normalized to one expected substitution per unit time, but what has
been studied in linguistics (largely in the context of the rigid assumptions of
‘glottochronology’, an early primitive, simplistic, and partly misguided attempt
at quantitative language classification) is the rate of losing cognates in the
basic vocabulary through time.

The clock rate $c$ in BEAST is the weighted mean of the rates of change. In a
binary substitution model with equilibrium frequencies `f[0]` and `f[1]`, this
gives us a normalizing factor $r$ such that

    r_{1→0} = f[0] × r
    r_{0→1} = f[1] × r
    f[0] × r_{0→1} + f[1] × r_{1→0} = c

Combining these three expressions, we can express the loss rate in terms of the
clock rate as

    r_{1→0} = c / (2 × f[1])

The studies that led rightly to the rejection of glottochronology showed that
the rate of change varies widely. Just like with the net diversification rate,
we can therefore estimate its order of magnitude from known language data, but
we cannot constrain it much beyond that. As such, the lognormal distribution is
again the distribution of choice.

```xml
<prior spec="Prior" id="ClockPrior" name="distribution">
  <x id="lossrate" spec="feast.expressions.ExpCalculator">
    <arg idref="clockrate" /><arg idref="freqParameter" />
    clockrate / (2 * freqParameter[1])
  </x>
  <distr spec="LogNormalDistributionModel">
```

Swadesh's rule-of-thumb of 20\% lexical
replacement over 1000 years implies

    (1-r)^{1000} = (1 - 20%)

so `r = 1- 0.8^{1/1000} = 2.23 × 10^-4`, while [@pagel2000history: 405] derives
a mean rate of `r = 6.1 × 10^-4` from his own data and a rate of `r = 5.8 ×
10^-4` from [@kruskal1971]. He also finds a factor of 3 between the slowest and
the fastest change in Malayo-Polynesian.

Translating these observations into parameters for the loss rate, the median of
these three estimates would give us a mean in log-space of `r = ln(5.8 × 10^-4)
= -7.45`.

```xml
    <parameter id="RealParameter.6" spec="parameter.RealParameter" estimate="false" name="M">-7.4524824544238095</parameter>
```

Taking the three estimates at face value, the (pseudo-corrected estimator of
the) standard deviation of their logarithms is 0.567, which puts the upper and
lower end of the 1σ interval, representing ca. 68% of the probability mass, at a
factor of 3.1 of each other – commensurate with the observations in
[@pagel2000history].

```xml
    <parameter id="RealParameter.7" spec="parameter.RealParameter" estimate="false" lower="0.0" name="S" upper="5.0">0.566676206191776</parameter>
  </distr>
</prior>
```

The last priors to specify concern the rate variation.
The rate for each concept follows a Gamma distribution, with a mean of 1.0 (so
the clock rate reflects the mean over all concepts and branches).

```xml
<plate var="concept" range="{partitions}">
  <prior spec="Prior" id="RateVariation:$(concept)" name="distribution" x="@speed:$(concept)">
    <distr spec="Gamma" id="Gamma:$(concept)" mode="OneParameter" alpha="@rateVariationGammaShape" />
  </prior>
</plate>

```
It is unclear what shape the Gamma distribution for the per-cognateset rates
should have, so we draw that shape from an exponential hyperprior with mean 1.


```xml
<prior spec="Prior" id="GammaShapePrior" name="distribution" x="@rateVariationGammaShape">
  <distr spec="Exponential" id="Exponential.0">
    <parameter id="RealParameter.0" spec="parameter.RealParameter" lower="0.0" name="mean" upper="0.0">1.0</parameter>
  </distr>
</prior>
</distribution>
```

## Model parameters


In summary, the model parameters and (their starting values) are as follows:

 - The central parameter is the phylogenetic tree, initialized with a random tree.
   ```xml
   <init id="startingTree" initial="@tree" taxonset="@taxa" spec="beast.evolution.tree.RandomTree">
     <populationModel spec="beast.evolution.tree.coalescent.ConstantPopulation">
       <popSize spec="parameter.RealParameter" value="10000" />
     </populationModel>
   </init>
   <state id="state" spec="State" storeEvery="5000">
     <tree id="tree" spec="beast.evolution.tree.Tree" name="stateNode" taxonset="@taxa">
       <trait id="dateTrait" spec="beast.evolution.tree.TraitSet" traitname="date-backward" taxa="@taxa" />
     </tree>
   ```

 - The substitution model is parameterized by the equilibrium frequencies of present vs. absent cognate classes
   ```xml
   <parameter id="freqParameter" spec="parameter.RealParameter" dimension="2" lower="0.0" name="stateNode" upper="1.0">0.9 0.1</parameter>
   ```
 - The FBD-SA tree prior is parameterized by net diversification rate, turnover, and two different sampling proportions (before 500yBP, and 500yBP until now)
   ```xml
   <parameter id="netDiversificationRate" spec="parameter.RealParameter" lower="0.0" name="stateNode" upper="10.0">0.0005</parameter>
   <parameter id="turnOver" spec="parameter.RealParameter" lower="0.0" name="stateNode" upper="1.0">0.2</parameter>
   <parameter id="SamplingProportion" spec="parameter.RealParameter" lower="0.0" name="stateNode" upper="1.0">0.2 0.2</parameter>
   ```
 - The strict clock is parameterized by a clock rate, which is constrained in terms of the loss rate.
   ```xml
   <parameter id="clockrate" spec="parameter.RealParameter" name="stateNode">0.0001</parameter>
   ```
 - The rate variation is parameterized using one parameter per concept, plus a hyper-prior which constrains the shape of the Gamma distribution.
   ```xml
   <plate var="concept" range="{partitions}">
     <parameter id="speed:$(concept)" spec="parameter.RealParameter" name="stateNode">1.0</parameter>
   </plate>
   <parameter id="rateVariationGammaShape" spec="parameter.RealParameter" name="stateNode">1.0</parameter>
   </state>
   ```

The tree has 39 tips and thus 77 different branch lengths (although with a high
number of pairwise dependencies among them). The model therefore has 84
continuous parameters and one tree topology parameter.

## Inference procedure

BEAST usually estimates the joint posterior probability of dated trees and other
parameters by Markov chain Monte Carlo sampling. However, nested sampling
[@maturana2019model] allows us to generate posterior samples at the same time as
marginal likelihood estimates. In order to estimate the model likelihood,
collect nested samples until we achieve a precision of 10^{-12}, or at most
50'000'000 samples in total.

As required by the NS procedure [@ns: section 4, p. 16 of the preprint], we
discard a particle in favour of a new one every 10000 steps: This is much more
than a factor of 10 higher than our number of parameters, and commensurate with
the rate at which a normal MCMC of comparable datasets gains additional
effective samples.

```xml
<run id="mcmc" spec="beast.gss.NS" chainLength="50000000" particleCount="3" epsilon="1e-12" numInitializationAttempts="1000" sampleFromPrior="false" init="@startingTree" subChainLength="10000">
  <distribution id="posterior" spec="util.CompoundDistribution">
    <distribution idref="prior" />
    <distribution idref="likelihood" />
  </distribution>
```

We track the weight and parameter values at the discarded points. This enables
us to get a posterior sample at no additional cost [@ns: section 2.7].

```xml
<logger id="tracelog" spec="NSLogger" fileName="vocabulary.log" logEvery="1" model="@posterior" sort="smart">
  <log idref="posterior" />
  <log idref="likelihood" />
  <log idref="prior" />
  <log id="TreeHeight" spec="beast.evolution.tree.TreeHeightLogger" tree="@tree" />
  <log idref="freqParameter" />
  <log idref="netDiversificationRate" />
  <log idref="turnOver" />
  <log idref="SamplingProportion" />
  <log idref="clockrate" />
  <log idref="lossrate" />
  <log idref="rateVariationGammaShape" />
</logger>
<logger id="screenlog" spec="NSLogger" logEvery="1">
  <log idref="posterior" />
  <log id="ESS.0" spec="util.ESS" arg="@posterior" />
  <log idref="likelihood" />
  <log idref="prior" />
</logger>
<logger id="treelog" spec="NSLogger" fileName="vocabulary.trees" logEvery="1" mode="tree">
  <log id="TreeWithMetaDataLogger" spec="beast.evolution.tree.TreeWithMetaDataLogger" tree="@tree" />
</logger>
```

## Operators

Each of the parameters must be modified for sampling, using at least one operator.

 - The tree topology is, as is usual, adjusted by a narrow and a wide exchange
   operator, and a Wilson-Balding operator. All three operators must be aware
   of the sampled ancestors in the tree. A special operator switches ancient
   tips between being leaves and sampled ancestors.
   > For a relaxed clock, there is a WilsonBaldingWithRateCategories
   ```xml
   <operator id="SampledAncestorJump" spec="LeafToSampledAncestorJump" removalProbability="@removalProbability" tree="@tree" weight="3.0" />
   <operator id="BirthDeathNarrow" spec="SAExchange" tree="@tree" weight="15.0" />
   <operator id="BirthDeathWide" spec="SAExchange" isNarrow="false" tree="@tree" weight="3.0" />
   <operator id="BirthDeathWilsonBalding" spec="SAWilsonBalding" tree="@tree" weight="1.0" />
   ```
 - The branch lengths are modified by scaling the entire tree, sliding subtrees
   (or just re-scaling the root), or a general uniform tree operator.
   > I have forgotten what the uniform tree operator does.
   ```xml
   <operator id="BirthDeathTreeScaler" spec="SAScaleOperator" scaleFactor="0.95" tree="@tree" weight="3.0" />
   <operator id="BirthDeathSubtreeSlide" spec="SubtreeSlide" tree="@tree" size="4" weight="15.0" />
   <operator id="BirthDeathTreeRootScaler" spec="SAScaleOperator" rootOnly="true" scaleFactor="0.6" tree="@tree" weight="2.0" />
   <operator id="BirthDeathUniformOperator" spec="SAUniform" tree="@tree" weight="30.0" />
   ```

 - Frequencies are adjusted using a dedicated exchange operator. This operator
   keeps the sum of both frequencies to 1.0, as appropriate for the model.
   ```xml
   <operator id="FrequenciesExchanger" spec="DeltaExchangeOperator" delta="0.003" weight="1.0" parameter="@freqParameter" />
   ```
 - The tree prior parameters each have their own scaling operator.
   ```xml
   <operator id="BirthRateScaler" spec="ScaleOperator" parameter="@netDiversificationRate" scaleFactor="0.9" weight="3.0" />
   <operator id="DeathRateScaler" spec="ScaleOperator" parameter="@turnOver" scaleFactor="0.9" weight="3.0" />
   <operator id="SamplingProportionScaler" spec="ScaleOperator" parameter="@SamplingProportion" scaleAllIndependently="true" scaleFactor="0.9" weight="3.0" />
   ```
 - The clock rate and gamma shape also individually adjusted by a scale operator.

   ```xml
   <operator id="StrictClockRateScaler" spec="ScaleOperator" parameter="@clockrate" scaleFactor="0.9" weight="4.0" />
   <operator id="gammaShapeScaler" spec="ScaleOperator" parameter="@rateVariationGammaShape" scaleFactor="0.5" weight="0.1" />
   ``` 

In addition, some of the parameters are strongly connected. Operators that
adjust a combination of parameters in a way that leaves likelihood or priors
roughly stable are useful for improved mixing behaviour of the Markov chain.
(The special sampled-ancestors behaviour of the scale operator only comes in
when scaling the root only, so we are fine using the basic up-down-operator here
and don't need a SA variant when scaling trees.)

 - Lower diversification rates fit better with longer trees, higher rates with
   shorter trees.
   ```xml
   <operator id="BirthRateUpDownOperator" spec="UpDownOperator" scaleFactor="0.9" weight="3.0" up="@netDiversificationRate" down="@tree" />
   ```
 - Even more directly, higher clock rate compensates for lower branch lengths.
   ```xml
   <operator id="strictClockUpDownOperator" spec="UpDownOperator" scaleFactor="0.9" weight="3.0" up="@clockrate" down="@tree" />
   ```

```xml
</run>
```
## ‘Glossary’

Beast allows us to define abbreviations for some frequent objects, such as re-curring probability distributions.
```xml
<map name="Normal">beast.math.distributions.Normal</map>
<map name="Uniform">beast.math.distributions.Uniform</map>
</beast>
```
