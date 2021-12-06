from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import copy

from utils import measure_violations
from mosek_solver import MOSEK_Solver
from iflipper_utils import init_cluster, get_zero_cluster, get_nonzero_two_clusters, transform_with_one_cluster, transform_with_two_clusters

class iFlipper:
    def __init__(self, label, w_sim, edge):
        """         
            Args: 
                label: Labels of the data
                w_sim: Similarity matrix
                edge: Indices of similar pairs
        """

        self.label = label
        self.w_sim = w_sim
        self.edge = edge

    def transform(self, m):
        """         
            Solves the optimization problem of minimally flipping labels given a limit to the number of individual fairness violations.

            Args: 
                m: The violations limit
                
            Return:
                flipped_label: Flipped labels for a given m
        """

        if measure_violations(self.label, self.edge) == m:
            flipped_label = self.label
        else:
            optimal_label = MOSEK_Solver(self.label, m, self.edge)
            converted_label = self.optimal_converting(optimal_label, self.label, self.edge)
            rounded_label = self.adaptive_rounding(converted_label, m, self.edge)
            flipped_label = self.reverse_greedy(self.label, rounded_label, m, self.w_sim, self.edge)

        return flipped_label
    
    def optimal_converting(self, optimal_label, label, edge):

        cluster_info, cluster_nodes, cluster_nodes_num = init_cluster(optimal_label, label, edge)
        T = len(cluster_info.keys())

        while T > 1:
            while True:
                alpha = get_zero_cluster(cluster_nodes_num)
                if alpha == 0:
                    break
                else:
                    cluster_info, cluster_nodes_num, cluster_nodes = transform_with_one_cluster(alpha, cluster_info, cluster_nodes_num, cluster_nodes)
                    T = len(cluster_info.keys())
            if T > 1:
                alpha, beta = get_nonzero_two_clusters(cluster_info)
                cluster_info, cluster_nodes_num, cluster_nodes = transform_with_two_clusters(alpha, beta, cluster_info, cluster_nodes_num, cluster_nodes)    
                T = len(cluster_info.keys())

        converted_label = copy.deepcopy(optimal_label)
        for value in cluster_nodes:
            for node in cluster_nodes[value]:
                converted_label[node] = value
        
        return converted_label

    def adaptive_rounding(self, converted_label, m, edge):
        """         
            Converts an optimal solution for the LP problem into a feasible solution whose values are only 0's ans 1's.

            Args: 
                opt_solution: Optimal solution for the LP problem where each value is one of {0, 1, alpha}
                m: The violations limit
                edge: Indices of similar pairs
                
            Return:
                rounded_label: Feasible binary integer solution
        """

        rounded_label = copy.deepcopy(converted_label)
        unique_values = np.unique(rounded_label)
        idx = (unique_values >= 1e-7) & (unique_values <= 1-1e-7)

        if np.sum(idx) >= 1:
            N0, N1 = 0, 0
            for (i, j) in edge:
                violation = abs(rounded_label[i] - rounded_label[j])
                if 1e-7 <= violation <= 1 - 1e-7:
                    if rounded_label[i] <= 1e-7 or rounded_label[j] <= 1e-7:
                        N0 += 1
                    elif rounded_label[i] >= 1-1e-7 or rounded_label[j] >= 1-1e-7:
                        N1 += 1

            index = (1e-7 < rounded_label) & (rounded_label < 1-1e-7)
            if N0 <= N1:
                rounded_label[index] = 1
            else:
                rounded_label[index] = 0

        return np.round(rounded_label)

    def reverse_greedy(self, original_label, rounded_label, m, w_sim, edge):
        """         
            Repeatedly unflips labels that increase the number of violations the least.

            Args: 
                original_label: Original labels
                rounded_label: Feasible binary integer solution from the adaptive rounding algorithm
                m: The violations limit
                w_sim: Similarity matrix
                edge: Indices of similar pairs
                
            Return:
                flipped_label: Flipped labels for a given m
        """

        flipped_label = copy.deepcopy(rounded_label)
        flipped_bool = (original_label != rounded_label)
        flipped_index = np.arange(len(rounded_label))[flipped_bool]

        num_violations = measure_violations(rounded_label, edge)
        while num_violations < m:
            flipped_label = copy.deepcopy(rounded_label)
            improvement_arr = []
            for j in range(len(rounded_label)):
                if flipped_bool[j]:
                    prev_y_diff = (rounded_label != rounded_label[j])
                    negative_improvement = - np.sum(w_sim[j] * (2 * prev_y_diff - 1))
                    improvement_arr.append(negative_improvement)

            sorted_index = np.argsort(improvement_arr)[:1]

            rounded_label[flipped_index[sorted_index]] = 1 - rounded_label[flipped_index[sorted_index]]
            flipped_bool[flipped_index[sorted_index]] = False
            flipped_index = np.arange(len(rounded_label))[flipped_bool]

            num_violations = measure_violations(rounded_label, edge)

        return flipped_label