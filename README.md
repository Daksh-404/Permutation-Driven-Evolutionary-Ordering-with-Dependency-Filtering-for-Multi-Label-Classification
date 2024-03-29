# Permutation Driven Evolutionary Ordering with Dependency Filtering for Multi-Label Classification(GenStaC)

Conducting trials on utilizing various evolutionary algorithms and techniques to solve Multi-Label Classification problem. A Problem Transformation approach is used with respect to the utilization of Evolutionary techniques for our classification purposes.

# Abstract

One of the key problems in Multi-Label Classification is label interdependence which is a critical factor
in determining the performance of a given multi-label classifier. This problem has been attempted through
the use of chaining (Classifiers are chained together) or Multi-Layered model architectures (Stacking based
approaches). However, these approaches neglect the order of labels while incorporating the label inter-
dependencies which in itself is a NP-Hard problem, neither do they provide space for partial-dependency
in a full-dependency architecture. Therefore, in this work, we use an Evolutionary approach to extract the
optimal label order for arranging the labels. We also propose novel crossover and mutation mechanisms
namely Ordered Slicing Crossover and Loop Shift Mutation. Furthermore, a Dependency Filtering Frame-
work is introduced to render partial dependency to avoid redundant labels and forced full dependency. Our
experiments were conducted on ten benchmark datasets with varying numbers of labels. Different perfor-
mance metrics were used to evaluate the effectiveness of the proposed method, and it was compared to other
state-of-the-art classifier models, showing an improvement of 14.46% on the best-ranked model to date. The
experiments also established reduced prediction time for the proposed approach.

# Introduction

Multi-Label Classification (MLC) is a specific instance of multi-class classification problems where a par-
ticular data point may belong to multiple classes. The goal of MLC is to learn the function that is able to
map input data point to their respective classes. MLC is especially applicable to the real world, where mem-
bership of objects is not exclusive to one class and where the very classes themselves are not atomic. Some
applications of MLC include - music categorization, image classification system, and bioinformatics.
MLC methods are divided into two categories: Algorithm Adaptation (AA) and Problem Transforma-
tion (PT). Algorithm Adaptation updates SLC methods in order for them to be utilized for multi-label
datasets, e.g., ML-kNN. On the other hand, PT transforms the MLC problem into SLC problems, in which
a single label is predicted using one model, thus making the number of classifiers used proportional to the
number of labels being predicted in the multi-label problem, e.g., Binary Relevance and Classifier Chains. Linear Ordering Problem (LOP) is an NP-hard combinatorial optimization problem, which in the
context of MLC means finding the optimal dependency preserving label order. The one-to-many mapping of
MLC means that the classes themselves can have dependencies, therefore ordering the labels and using class
membership as a feature to determine membership in successive classes is a viable approach to MLC. Since
LOP approaches still requires an underlying architecture, that is where Stacking methods come in. Stacking
methods have a two-tier classifier architecture with multiple variations in terms of their correlation strategies.
Stacked Chaining is a high-order Stacking method that manages the problem of no interdependence of
labels at both levels of the Stacking MLC structure using the method of Chaining at both levels. It
incorporates label dependence at both levels and ensures full label dependence in this multi-label classifier
through the use of Chaining at both levels. Out of the three variants of StaC viz. StaCv1, StaCv2, StaCv3,
this paper uses StaCv1 which tackles LOP using hamming loss leaving scope for improvement. However,
there are issues with such a multi-level chained structure as follows:

- Label Ordering plays a crucial role in the performance of classifiers using the Chaining method, as
it allows to model labels semantics reducing label-set and hypercube sparsity.However, StaC
provides no approach to handle label ordering.
- Full label dependence on previous labels lead to forced dependencies which negatively affect the per-
formance by leading to the development of complex, intricate mappings.
- Higher linkage dependencies lead to elevated data complexity in the network, encumbering the system
with heavy computational tasks.
- Longer the chain, the more are the chances of error propagation if proper label ordering is not supplied.

This paper addresses both the above-mentioned issues using the proposed method called GenStaC to
improve on these existing problems. In this approach, the ordering of labels on both levels of StaCv1 (a
chosen variant for the study) is decided by Label Order Optimization Scheme (LooS) (Evolutionary approach)
in which we introduce a new crossover (Ordered Slicing Crossover Mechanism (OSCM)) and mutation(Loop
Shift Mutation (LSM)) mechanisms. In order to render selective partial dependency, a Dependency Filtering
Framework (DFF), a filter-based feature selection approach, is used teliminate redundant dependencies.
We adopt LooS and DFF approaches to develop GenStaC. It works in mainly two stages. In the first stage
LooS generates optimal label orderings for b labels which are dependent on the dataset. In the second stage,
this optimal label ordering is supplied to StaCv1 which adopts DFF during each step of the chain on both
levels. Thus the contributions of this paper are as follows:

- It incorporates an Evolutionary approach for permutations called LooS, to find the optimal label order
for both levels of Stacked Chaining (StaCv1 ).
- It utilizes Mutual Information Matrix as the fitness function in LooS. This has not been utilized in the
past for solving Linear Ordering Problems as per our knowledge.
- A selective partial dependence called DFF is instated to avoid a complete full-label dependence. This
ensures only important, relevant, and quality dependencies are used during classification.
- Proposing a new crossover (OSCM) and mutation(LSM) mechanism for permutation-based-chromosomes.
OSCM maintains the order while combining parents, to maintain important sub-permutation orders.
LSM ensures that important permutations are maintained and relative cyclic order is maintained in
permutation cycles.

# Methodology

The proposed algorithm has been broken into two parts: Label Order Optimization Scheme and Filtered Stacked Chaining for an easier understanding of the overall approach.

### Label Order Optimization Scheme(LooS)

We discussed the use of Evolutionary approaches on Label Order Problems. Thus we take inspiration
from the design of the Genetic Algorithm and concoct a solution for the label ordering problem through the
following steps. The Mutual Information matrix is used as the fitness function, which is to be optimized to obtain optimal label
order. Once the fitness values are calculated, we select a roster of parents through Roullete Wheel
Selection. GenStaC then performs OSCM and LSM which have been discussed in the previous sections. At
the end of a generation, we use the elitism rate which governs the percentage of offspring to the percentage
of parents from the previous generation that is selected while constructing the population for the next
generation. For this particular example, we take the elitism rate as 2, thus selecting the fittest two parents
and four fittest offspring.

### Dependency Filtering Framework
It was observed that StaC uses full dependency, which coerces a lot of redundant and useless dependencies while predicting a label. Since there are so many linkages between the previous labels, the existing features, and the label being predicted, this leads to an overload of dependencies and forces the model to develop complex, non-linear relationships while mapping the inputs to the outputs. This led to the idea of introducing a dependency filtering mechanism that can remove not only irrelevant features but also useless (previously generated) labels.

### GenStaC (StaCv1 + LooS + DFF)
Once we obtain the supposed label ordering from the LooS, we supply that ordering to the Stac itself. We use the StaCv1 variant of StaC which utilizes label ordering and manages it through the use of Hamming Loss. However using Hamming Loss for calculating label ordering is sub-optimal, and Evolutionary approaches have proved to be better at providing optimal solutions to such problems. Also, the best approach out of all the variants is StaCv2 as clearly mentioned in their paper. This particular variant doesn’t employ any form of label ordering. This piques interest in observing how LooS which employs a technique to identify the optimal label ordering, can outperform StaCv2, suggesting the importance of label ordering. In this part of the algorithm, we introduce the modified StaC structure - Filtered StaC. It takes the label order supplied by the LooS, and orders the label classifiers at both levels using the same. At each step of classification at both levels, DFF is applied while generating predictions for the target variable. Thus we can say GenStaC i the combined application of LooS and DFF on StaCv1, which culminates into our final model architecture. The highlighted parts denote the proposed modifications to the base approach. We take the input of a dataset D, which contains features X and labels Y . The parameters that define the inputs to the proposed evolutionary approach have also been added as inputs namely, Population Size, Elitism Rate, Mutation, and Crossover Probability and Number of Generations it will run for. The output is the set of two classifiers for the first and second levels respectively.

![method](research_arch.drawio-1.png)

# Results

### Performance Comparision
![plot](plot.jpeg)

### Dunn Test
![dunn](dunn_test.png)


