# iFlipper: Label Flipping for Individual Fairness

## Abstract
As machine learning becomes prevalent, mitigating any unfairness present in the training data becomes critical. Among the various notions of fairness, this paper focuses on the well-known individual fairness where similar individuals must be treated similarly. While individual fairness can be improved when training a model (inprocessing), we contend that fixing the data before model training (pre-processing) is a more fundamental solution. In particular, we show that label flipping is an effective pre-processing technique for improving individual fairness. Our system iFlipper solves the optimization problem of minimally flipping labels given a limit to the number of individual fairness violations, where a violation occurs when two similar examples in the training data have different labels. We first prove that the problem is NP-hard. We then propose an approximate linear programming algorithm and provide theoretical guarantees on how close its result is to the optimal solution in terms of the number of label flips. We also propose techniques for making the solution to the linear programming more optimal without exceeding the violations limit. Experiments on real datasets show that iFlipper significantly outperforms other pre-processing baselines in terms of individual fairness and accuracy on unseen test sets. In addition, iFlipper can be combined with in-processing techniques for even better results.

## Label flipping

<p align="center"><img src=https://user-images.githubusercontent.com/29707304/144565505-4704eec2-fdb2-42f9-8723-d375cd3ebd15.png></p>

We propose label flipping as a way to mitigate data bias for individual fairness and assume a binary classification setting where labels have 0 or 1 values. Given a training set of examples, the idea is to change the labels of some of the examples such that similar examples have the same labels as much as possible. We can use a graph representation to illustrate label flipping as shown in the above figure. Each node represents a training example, and it color indicates the label (black indicates label 1, and white indicates 0). Two similar nodes are connected with an edge, and a violation occurs when the edge is connected with two nodes with different labels. In the figure, there are four nodes where only the nodes 1, 2, and 3 are similar to each other. In addition, nodes 1 and 4 have label 1, and nodes 2 and 3 have label 0. We can see that there are two “violations” of fairness in this dataset: (1,2) and (1,3) because there are edges between them, and they have different colors. After flipping the label of node 1 from 1 to 0, we have no violations.

## Label Flipping Optimization Problem

One consequence of label flipping is an accuracy-fairness trade-off where the model’s accuracy may diminish. As an extreme example, if we simply flip all the labels to be 0, then a trained model that only predicts 0 is certainly fair, but inaccurate to say the least. Even if we carefully flip the labels, we still observe a trade-off. We thus formulate the optimization problem where the objective is to minimize the number of label flipping while limiting the number of individual fairness violations to an allowed number m. The optimization can be formally stated as an instance of mixed-integer quadratic programming (MIQP) problem, and we prove that it is NP-hard.

<p align="center"><img src=https://user-images.githubusercontent.com/29707304/144567341-b0dc73a9-df37-402d-8cd8-db181df91b7d.png width="550"></p>

y<sub>i</sub> and y<sup>'</sup><sub>i</sub>

## iFlipper

iFlipper converts the MIQP problem into an approximate linear program (LP) problem and produces a feasible solution with theoretical guarantees. The conversion is done in
two steps: from MIQP to an equivalent integer linear program (ILP) using linear constraints and from the ILP problem to an approximate LP problem. iFlipper then solves the approximate LP problem and convert its optimal solution to another optimal solution that only has values in {0, 𝛼, 1} using the converting algorithm. iFlipper then applies adaptive rounding to ensure feasibility. Finally, iFlipper possibly improves the rounded solution by unflipping labels using using the reverse greedy algorithm.
