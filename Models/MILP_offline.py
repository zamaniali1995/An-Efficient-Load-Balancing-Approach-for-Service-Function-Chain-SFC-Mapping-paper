#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Siun Jan 27 16:44:41 2019
@author: ali(zamaniali1995@gmail.com)
"""
from coopr.pyomo import *
import time
# import pyomo.environ as pyo
import InputConstants
import matplotlib.pyplot as plt


# Must be changed
class MILP_offline_model:
    def __init__(self, k, alpha):
        self.input_cons = InputConstants.Inputs()
        self.k = k
        self.alpha = alpha
        
    def run(self, graph, chains, functions):
        start_time =time.time()
        # nodes_num = graph.nodes_num()
        # funcs_num = chains.functions_num()
        # chains_num = chains.chains_num()
        # sou_num = node_num
        # dist_num = node_num
        M = 100000
        # K_path_num = 2
        # chain_num = 3
        # source_distinations = [
        #     [(1, 1), (2, 14), (3, 13)], 
        #     [(1, 1), (2, 14), (3, 13)],
        #     [(1, 1), (2, 14), (3, 13)],
        # ]
        # k_path = {
        #     (1, 1): [(1, 2, 1), (1, 3, 1)],
        #     (2, 14): [(2, 3, 5, 14), (2, 3, 6, 14)],
        #     (3, 13): [(3, 4, 5, 13), (3, 4, 6, 13)]
        # }

        ##########################################
        # Define concrete model
        ###########################################
        model = ConcreteModel()

        ###########################################
        # Sets
        ###########################################
        # Set of nodes: v
        model.V = graph.nodes_name
        # Set of functions: F
        model.F = range(functions.num())
        # Set of chains: C
        model.C = range(chains.num())
        # # Set of sources: S
        # model.S = []
        # for c in range(chains_num):
        #     for i in range(len(chains[c].users)):
        #         model.S.append(chains[c].users[i][0])
        model.S = graph.node_name_list
        # Set of distinations: D
        # model.D = []
        # for c in range(chain_num):
        #     for i in range(len(chains[c].users)):
        #         model.D.append(chains[c].users[i][1])
        model.D = graph.node_name_list
        # Set of K shortest paths: K_sd
        model.k_path = graph.k_path
        # Set of k paths
        model.P = range(self.k)
        # Set of function of each chain
        # nc = []
        model.nc = []
        for c in model.C:
            # nc.append(chains.users_number(chains.chains_list[c].name))
            model.nc.append(chains.funs_num(chains.chains_list[c].name))
            # model.nc.append(tmp)
        # cpus usage of each function
        model.nf = []
        for f in functions.functions_list.keys():
            model.nf.append(functions.cpu_usage(f))
        # mem usage of each function
        model.mf = []
        for f in functions.functions_list.keys():
            model.mf.append(functions.mem_usage(f))
        # model.nf = nf
        # model.i(C) = 
        # Set of users

        model.L = range(graph.links_num())
        model.R = []
        for c in model.C:
            model.R.append(chains.chains_list[c].users)
            # Nodes capacity
        # model.n = graph.node_list[0].cap
        # Set of IDs
        flag = 0
        model.phi = {}
        for c in model.C:
            for (s, d) in model.R[c]:
                P = model.k_path(s, d, self.k)
                for p in range(len(P)):
                    for l in model.L:
                        flag = 0
                        for n in range(len(P[p]) - 1):
                            # print(len(path))
                            # for n in range(len(path)-1):
                            if (model.k_path(s, d, self.k)[p][n], model.k_path(s, d, self.k)[p][n + 1])\
                                    == graph.link_list[l].name:
                                model.phi[(l, p, s, d)] = 1
                                flag = 1
                            elif flag == 0:
                                model.phi[(l, p, s, d)] = 0
        model.I = {}
        # I = {}
        for c in model.C:
            for f_num, f_name in enumerate(functions.functions_list.keys()):
                for i in range(model.nc[c]):
                    if chains.chains_list[c].fun[i] == f_name:
                        # I[(f_num, i, c)] = 1
                        model.I[(f_num, i, c)] = 1
                    else:
                        # I[(f_num, i, c)] = 0
                        model.I[(f_num, i, c)] = 0
        # print(model.I)
        ###########################################
        # Variables
        ###########################################
        max_of_chain_function = max([model.nc[c] for c in model.C])
        model.t = Var(within=NonNegativeReals)
        model.t_prime = Var(within=NonNegativeReals)
        model.a = Var(model.V, model.C, model.P, range(max_of_chain_function), model.S, model.D, within=Binary)
        # model.a = Var('1', model.C, model.F, within= Binary)
        # model.a = Var('2', model.C, model.F, within= Binary)
        # Var('1', model.C, model.F, within= Binary).pprint()
        # model.a.pprint()
        # model.a_ = {}
        # for v in model.V:    
        #     for c in model.C:
        #         for (s, d) in model.R[c]:
        #             # model.add_component(model.a, Var(v, str(c), model.P, range(model.nc[c]), s, d, within=Binary)) 
        #             model.add_component(model.a_[v, c, s, d], Var(v, str(c), model.P, range(model.nc[c]), s, d, within=Binary))
                    # model.del_component(model.a)
        # model.add_component(model.a_)
                    # model.a_[v, c, s, d].pprint()
            #         for p in model.P:
            #             for nc in range(model.nc[c]):
                            # model.a.append(Var(v, c, p, nc, s, d))
                            # model.a[v, c, p, nc, s, d,] = Var(within=Binary)
                # model.a = Var(model.V, model.C, model.p, model.nc[0], model.S, model.D, within=Binary)
        # model.b = {}
        
        # for c in model.C:
        #     for (s, d) in model.R[c]:
        #         model.b[(c, s, d)] = Var(model.P, c, s, d, within=Binary)
                # model.b[c, s, d].pprint()
                    # model.b[p, c, s, d] = Var(within=Binary)
        model.b = Var(model.P, model.C, model.S, model.D, within=Binary)
        # model.d = [] * 4
        # for c in model.C:
        # model.d = Var(model.nc[0], model.C, model.S, model.D, within= Binary)
        ###########################################
        # Objective function: min. t
        ###########################################
        model.obj = Objective(expr=self.alpha * model.t + (1 - self.alpha) * model.t_prime
                              , sense=minimize)

        ###########################################
        # Constraints
        ##########################################
        # 1st constraint
        model.balance_CPU_cons = ConstraintList()
        for v_num, v in enumerate(model.V):
            model.balance_CPU_cons.add(sum([model.a[v, c, p, i, s, d] *
                                            model.I[(f, i, c)] *
                                            model.nf[f] *
                                            chains.chains_list[c].tra /
                                            graph.node_list[v_num].cap_cpu
                                            for c in model.C
                                            for s, d in model.R[c]
                                            for p in model.P
                                            for i in range(model.nc[c])
                                            for f in model.F
                                            ]) <= model.t
                                       )
        # # 2nd constraint
        # model.balance_memory_cons = ConstraintList()
        # for v_num, v in enumerate(model.V):
        #     model.balance_memory_cons.add(sum([model.a[v, c, p, i, s, d] *
        #                                        model.I[(f, i, c)] *
        #                                        model.mf[f] *
        #                                        chains.chains_list[c].tra /
        #                                        graph.node_list[v_num].cap_mem
        #                                        for c in model.C
        #                                        for s, d in model.R[c]
        #                                        for p in model.P
        #                                        for i in range(model.nc[c])
        #                                        for f in model.F
        #                                        ])
        #                                   <=
        #                                   model.t)

        # 2nd constraint
        model.node_CPU_cap_cons = ConstraintList()
        for v_num, v in enumerate(model.V):
            model.node_CPU_cap_cons.add(sum([model.a[v, c, p, i, s, d] *
                                             model.I[(f, i, c)] *
                                             model.nf[f] *
                                             chains.chains_list[c].tra /
                                             graph.node_list[v_num].cap_cpu
                                             for c in model.C
                                             for (s, d) in model.R[c]
                                             for p in model.P
                                             for i in range(model.nc[c])
                                             for f in model.F
                                             ]) <= 1 
                                        )

        model.node_memory_cap_cons = ConstraintList()
        for v_num, v in enumerate(model.V):
            model.node_memory_cap_cons.add(sum([model.a[v, c, p, i, s, d] *
                                                model.I[(f, i, c)] *
                                                model.mf[f] *
                                                chains.chains_list[c].tra /
                                                graph.node_list[v_num].cap_mem
                                                for c in model.C
                                                for (s, d) in model.R[c]
                                                for p in model.P
                                                for i in range(model.nc[c])
                                                for f in model.F
                                                ])
                                           <=
                                           1)

        # 3rd constraint
        model.link_balance_cons = ConstraintList()
        for l in model.L:
            model.link_balance_cons.add(sum([model.b[p, c, s, d] *
                                            model.phi[(l, p, s, d)] *
                                            chains.chains_list[c].tra /
                                            graph.link_list[l].ban
                                            for c in model.C
                                            for (s, d) in model.R[c]
                                            for p in range(len(model.k_path(s, d, self.k)))
                                            ])
                                           <=
                                           model.t_prime
                                           )
        # 3rd constraint
        # model.link_cap_cons = ConstraintList()
        # for l in model.L:
        #     model.link_cap_cons.add(sum([model.b[p, c, s, d] *
        #                                  model.phi[(l, p, s, d)] *
        #                                  chains.chains_list[c].tra / 
        #                                  graph.link_list[l].ban
        #                                  for c in model.C
        #                                  for (s, d) in model.R[c]
        #                                  for p in model.P
        #                                  ]) <= 1
        #                                )
        # 4th constraint
        model.path_selection_cons = ConstraintList()
        for c in model.C:
            for (s, d) in model.R[c]:
                model.path_selection_cons.add(sum([model.b[p, c, s, d]
                                                   for p in range(len(model.k_path(s, d,self.k)))
                                                   ]) == 1
                                              )
        # 5th constraint
        # model.satisfy_req_1_cons = ConstraintList()
        # for c in model.C:
        #     for (s, d) in model.R[c]:
        #         for i in model.nc[c]:
        #             for p in range(len(k_path[(s, d)])):
        #                 model.satisfy_req_1_cons.add(sum([
        #                     model.a[v, c, i, s, d]  
        #                     for v in model.k_path[(s, d)][p]

        #                 ])
        #                 <=
        #                 1 + M * (1 - model.b[p, c, s, d])
        #                 )
        # 5th constraint
        model.satisfy_req_2_cons = ConstraintList()
        for c in model.C:
            for (s, d) in model.R[c]:
                for p in model.P:
                    for i in range(model.nc[c]):

                        model.satisfy_req_2_cons.add(sum([
                            model.a[v, c, p, i, s, d]
                            for v in model.V
                            # for v in model.k_path[(s, d)][p]

                        ])
                                                     <=
                                                     model.b[p, c, s, d]
                                                     # 1 - M * (1 - model.b[p, c, s, d])
                                                     )

        model.satisfy_req_3_cons = ConstraintList()
        for c in model.C:
            for (s, d) in model.R[c]:
                P = model.k_path(s, d, self.k)
                for p in range(len(P)):
                    for i in range(model.nc[c]):
                        model.satisfy_req_3_cons.add(sum([
                            model.a[v, c, p, i, s, d]
                            # for v in model.V
                            for v in P[p]

                        ])
                                                     >=
                                                     model.b[p, c, s, d]
                                                     # 1 - M * (1 - model.b[p, c, s, d])
                                                     )
        # 5th constraint
        # model.satisfy_req_1_cons = ConstraintList()
        # for c in model.C:
        #     for (s, d) in model.R[c]:
        #         model.satisfy_req_1_cons.add(sum([model.d[i, c, s, d]
        #                                         for i in model.nc[c]
        #                                         ])
        #                                         == 
        #                                         nc[c]
        #                                         )
        # # 6th constraint:
        # model.satisfy_req_2_cons = ConstraintList()
        # for c in model.C:
        #     for (s, d) in model.R[c]:
        #         for i in model.nc[c]:
        #             model.satisfy_req_2_cons.add(sum([
        #                 model.a[v, c, f, s, d] * model.I[(f, i, c)]
        #                                     for v in model.V
        #                                     for f in model.F
        #             ])
        #              <=
        #             model.d[i, c, s, d])
        # # 7th constraint:
        # model.satisfy_req_3_cons = ConstraintList()
        # for c in model.C:
        #     for (s, d) in model.R[c]:
        #         for f in model.F:
        #             model.satisfy_req_3_cons.add(sum([
        #                 model.d[i, c, s, d] * model.I[(f, i, c)]
        #                 for i in model.nc[c]
        #             ])
        #             <=
        #             sum([
        #                 model.a[v, c, f, s, d]
        #                 for v in model.V
        #             ])
        #             )
        # # 8th constraint:
        # model.deploy_on_path_cons = ConstraintList()
        # for c in model.C:
        #     for (s, d) in model.R[c]:
        #         for p in model.p:
        #             if len(k_path[(s, d)]) >= p + 1:
        #                 model.deploy_on_path_cons.add(sum([
        #                     model.a[v, c, f, s, d]
        #                     for v in k_path[(s, d)][p]
        #                     for f in model.F
        #             ])
        #             <= 
        #             model.b[p, c, s, d]
        #             )
        # 9th constraint:
        model.seq_cons = ConstraintList()
        for c in model.C:
            for (s, d) in model.R[c]:
                P = model.k_path(s, d, self.k)
                for p in range(len(P)):
                    for i in range(model.nc[c] - 1):
                        for v_num, v in enumerate(P[p]):
                            if v_num != 0:
                                model.seq_cons.add(sum([
                                    model.a[v_1, c, p, i_1, s, d]
                                    for v_1 in model.k_path(s, d, self.k)[p][: v_num]
                                    for i_1 in range(i + 1, model.nc[c])
                                ])
                                                   <=
                                                   M * (2 - model.b[p, c, s, d] - model.a[v, c, p, i, s, d])
                                                   )
        # model.seq_1_cons = ConstraintList()
        # for c in model.C:
        #     for (s, d) in model.R[c]:
        #         for p in range(len(model.k_path[(s, d)])):
        #             for i in range(nc[c] - 1):
        #                 for v_num, v in enumerate(model.k_path[(s, d)][p]):
        #                     if v_num != 0:
        #                         model.seq_1_cons.add(sum([
        #                             model.a[v_1, c, i_1, s, d]
        #                             for v_1 in model.k_path[(s, d)][p][: v_num]
        #                             for i_1 in range(i+1, nc[c])
        #                         ])
        #                         >=
        #                         - M * (2 - model.b[p, c, s, d] - model.a[v, c, i, s, d])
        #                         )

        # model.pprint()
        # # 2nd constraint
        # model.path_cons = ConstraintList()
        # for c in model.C:
        #     for sd in chains[c].users:
        #         s = sd[0]
        #         d = sd[1]
        #         model.path_cons.add(sum([model.b[s, d, p, c] for p in model.K_sd]) == 1)
        # model.balance_cons.pprint()
        # model.link_balance_cons.pprint()
        opt = SolverFactory("cplex", executable="/opt/ibm/ILOG/CPLEX_Studio128/cplex/bin/x86-64_linux/cplex")
       #  opt.options["threads"] = 2
        results = opt.solve(model)

        # model.pprint()
        node_cpu_cap = []
        node_mem_cap = []
        cpu = 0
        mem = 0
        for v_num, v in enumerate(model.V):
            for c in model.C:
                for (s, d) in model.R[c]:
                    for p in model.P:
                        for i in range(model.nc[c]):
                            for f in model.F:

                            # print(value(model.a[v, c, i, s, d]))
                                cpu += value(model.a[v, c, p, i, s, d]) * model.I[(f, i, c)] * model.nf[f] * chains.chains_list[c].tra
                                mem += value(model.a[v, c, p, i, s, d]) * model.I[(f, i, c)] * model.mf[f] * chains.chains_list[c].tra
            node_cpu_cap.append(cpu / graph.node_list[v_num].cap_cpu * 100)
            node_mem_cap.append(mem / graph.node_list[v_num].cap_mem *100)
            cpu = 0
            mem = 0
        link = 0
        link_cap = []
        for l in model.L:
            for c in model.C:
                for (s, d) in model.R[c]:
                    for p in range(len(model.k_path(s, d, self.k))):
                        link += value(model.b[p, c, s, d]) * model.phi[(l, p, s, d)] * chains.chains_list[c].tra
            link_cap.append(link / graph.link_list[l].ban * 100)
            link = 0
        link_name = []
        for l in model.L:
            link_name.append(l)
        # print(link_cap)
        # model.a.pprint()
        # model.b.pprint()
        # print(model.phi)
        # model.a.pprint()
        # model.b.pprint()
        # model.path_selection_cons.pprint()
        # model.balance_cons.pprint()
        # model.seq_cons.pprint()
        # model.b.pprint()
        # model.a.pprint()
        # print(I)
        # print(k_path[("1", "2")])
        # print(node_cap)
        # # print(results)
        end_time = time.time()
        # print("ILP time:", end_time-start_time)
        # with open('./Results/ILP/ILP_cpu.txt', 'w') as f:
        #     print(node_cpu_cap, file=f)
        #     print("max of cpu usage", max(node_cpu_cap), file=f)
        #     print("sum of cpu usage", sum(node_cpu_cap), file=f)
        # with open('./Results/ILP/ILP_memory.txt', 'w') as f:
        #     print(node_mem_cap, file=f)
        #     print("max of cpu usage", max(node_mem_cap), file=f)
        #     print("sum of cpu usage", sum(node_mem_cap), file=f)
        # with open('./Results/ILP/ILP_link.txt', 'w') as f:
        #     print(link_cap, file=f)
        #     print("bandwidth consumption : ", sum(link_cap), file=f)
        #     print("max of link bandwidth : ", max(link_cap), file=f)
        #     print("avg of link consumption: ", sum(link_cap) / len(link_cap), file=f)
        # with open('./Results/ILP/ILP_info.txt', 'w') as f:
        #     print('time:', end_time-start_time, file=f)
        #     print('k_path:', self.input_cons.k_path_num, file=f)
        #     print('alpha:', self.input_cons.alpha, file=f)
        # print("MILP_offline", sum(node_cpu_cap))
        return(max(node_cpu_cap), max(link_cap), end_time - start_time)
        # plt.bar(graph.node_name_list, node_cpu_cap)
        # plt.show()
        # plt.savefig('result_cpu_ILP.png')
        # plt.close()
        # plt.bar(graph.node_name_list, node_mem_cap)
        # plt.show()
        # plt.savefig('result_mem_ILP.png')
        # plt.close()

        # plt.bar(link_name, link_cap)
        # plt.show()
        # plt.savefig('result_link_ILP.png')
        # plt.close()
        # model.satisfy_req_1_cons.pprint()
        # print(model.balancke_cons)


# class CG_Model:
#     def __init__(self):
#         self.input_cons = InputConstants.Inputs()
#         self.theta = {}

#     def create(self, graph, functions, chains, k_path):
#         dual = [0.001, 0.001, 0.001, 0.001, 0.001, 1, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
#         for i in range(4):
#             print("iteration:", i)
#             theta = self.__pricing(dual, graph, functions, chains, k_path)
#             print("pricing done")
#             # print(theta)
#             # print(theta)
#             dual, node_cap = self.__master(i, theta, graph, functions, chains, k_path)
#             # print(dual)
#             # print(self.theta)
#         plt.bar(graph.node_name_list, node_cap)
#         plt.show()
#         plt.savefig('result_CG.pdf')

#     def __pricing(self, _lambda, graph, functions, chains, k_path):
#         node_num = len(graph.node_list)
#         func_num = len(functions)
#         chain_num = len(chains)
#         sou_num = node_num
#         dist_num = node_num
#         M = 10000000
#         ##########################################
#         # Define concrete model
#         ###########################################
#         model = ConcreteModel()

#         ###########################################
#         # Sets
#         ###########################################
#         # Set of nodes: v
#         model.V = graph.node_name_list
#         # Set of functions: F
#         model.F = range(func_num)
#         # Set of chains: C
#         model.C = range(chain_num)
#         # Set of sources: S
#         model.S = []
#         for c in range(chain_num):
#             for i in range(len(chains[c].users)):
#                 model.S.append(chains[c].users[i][0])
#         # model.S = graph.node_name_list
#         # Set of distinations: D
#         model.D = []
#         for c in range(chain_num):
#             for i in range(len(chains[c].users)):
#                 model.D.append(chains[c].users[i][1])
#         # model.D = graph.node_name_list
#         # Set of K shortest paths: K_sd
#         model.k_path = k_path
#         # Set of k paths
#         model.p = range(self.input_cons.k_path_num)
#         # Set of function of each chain
#         nc = []
#         model.nc = []
#         for c in range(chain_num):
#             nc.append(len(chains[c].fun))
#             tmp = range(len(chains[c].fun))
#             model.nc.append(tmp)
#         model.nf = []
#         for f in functions.keys():
#             model.nf.append(functions[f])
#         # model.nf = nf
#         # model.i(C) = 
#         # Set of users
#         model.R = []
#         for c in range(chain_num):
#             model.R.append(chains[c].users)
#             # Nodes capacity
#         model.n = graph.node_list[0].cap
#         # Set of IDs
#         model.I = {}
#         I = {}
#         for c in range(chain_num):
#             for f_num, f_name in enumerate(functions.keys()):
#                 for i in range(nc[c]):
#                     if chains[c].fun[i] == f_name:
#                         I[(f_num, i, c)] = 1
#                         model.I[(f_num, i, c)] = 1
#                     else:
#                         I[(f_num, i, c)] = 0
#                         model.I[(f_num, i, c)] = 0
#         # print(model.I)
#         ###########################################
#         # Variables
#         ###########################################
#         model.x = Var(model.V, within=NonNegativeReals)
#         # model.a = Var(model.V, model.C, model.F, model.S, model.D, within= Binary)
#         model.a = Var(model.V, model.C, model.p, model.nc[0], model.S, model.D, within=Binary)
#         model.b = Var(model.p, model.C, model.S, model.D, within=Binary)
#         # model.d = [] * 4
#         # for c in model.C:
#         # model.d = Var(model.nc[0], model.C, model.S, model.D, within= Binary)
#         ###########################################
#         # Objective function: min. t
#         ###########################################
#         model.obj = Objective(expr=sum([
#             _lambda[v_num] * model.x[v]
#             for v_num, v in enumerate(model.V)
#         ]), sense=maximize)
#         # plt.show()

#         ###########################################
#         # Constraints
#         ##########################################
#         model.first_cons = ConstraintList()
#         for v in model.V:
#             model.first_cons.add(sum([model.a[v, c, p, i, s, d] *
#                                       model.I[(f, i, c)] *
#                                       model.nf[f] *
#                                       1

#                                       for c in model.C
#                                       for (s, d) in model.R[c]
#                                       for i in model.nc[c]
#                                       for f in model.F
#                                       for p in model.p
#                                       ])
#                                  ==
#                                  model.x[v])
#         # 2nd constraint
#         model.node_cap_cons = ConstraintList()
#         for v in model.V:
#             model.node_cap_cons.add(sum([model.a[v, c, p, i, s, d] *
#                                          model.I[(f, i, c)] *
#                                          model.nf[f] *
#                                          1

#                                          for c in model.C
#                                          for (s, d) in model.R[c]
#                                          for i in model.nc[c]
#                                          for f in model.F
#                                          for p in model.p
#                                          ])
#                                     <=
#                                     model.n)
#         # 3rd constraint

#         # 4th constraint
#         model.path_selection_cons = ConstraintList()
#         for c in model.C:
#             for (s, d) in model.R[c]:
#                 model.path_selection_cons.add(sum([model.b[p, c, s, d]
#                                                    for p in range(len(model.k_path[(s, d)]))
#                                                    ])
#                                               ==
#                                               1
#                                               )
#         # 5th constraint
#         model.satisfy_req_1_cons = ConstraintList()
#         for c in model.C:
#             for (s, d) in model.R[c]:
#                 for i in model.nc[c]:
#                     for p in range(len(k_path[(s, d)])):
#                         model.satisfy_req_1_cons.add(sum([
#                             model.a[v, c, p, i, s, d]
#                             for v in model.V

#                         ])
#                                                      <=
#                                                      model.b[p, c, s, d]
#                                                      )
#                 # 5th constraint
#         model.satisfy_req_2_cons = ConstraintList()
#         for c in model.C:
#             for (s, d) in model.R[c]:
#                 for i in model.nc[c]:
#                     for p in range(len(k_path[(s, d)])):
#                         model.satisfy_req_2_cons.add(sum([
#                             model.a[v, c, p, i, s, d]
#                             for v in model.k_path[(s, d)][p]

#                         ])
#                                                      >=
#                                                      1 - M * (1 - model.b[p, c, s, d])
#                                                      )

#         model.seq_cons = ConstraintList()
#         for c in model.C:
#             for (s, d) in model.R[c]:
#                 for p in range(len(model.k_path[(s, d)])):
#                     for i in range(nc[c] - 1):
#                         for v_num, v in enumerate(model.k_path[(s, d)][p]):
#                             if v_num != 0:
#                                 model.seq_cons.add(sum([
#                                     model.a[v_1, c, p, i_1, s, d]
#                                     for v_1 in model.k_path[(s, d)][p][: v_num]
#                                     for i_1 in range(i + 1, nc[c])
#                                 ])
#                                                    <=
#                                                    M * (2 - model.b[p, c, s, d] - model.a[v, c, p, i, s, d])
#                                                    )
#         # model.seq_1_cons = ConstraintList()
#         # for c in model.C:
#         #     for (s, d) in model.R[c]:
#         #         for p in range(len(model.k_path[(s, d)])):
#         #             for i in range(nc[c] - 1):
#         #                 for v_num, v in enumerate(model.k_path[(s, d)][p]):
#         #                     if v_num != 0:
#         #                         model.seq_1_cons.add(sum([
#         #                             model.a[v_1, c, i_1, s, d]
#         #                             for v_1 in model.k_path[(s, d)][p][: v_num]
#         #                             for i_1 in range(i+1, nc[c])
#         #                         ])
#         #                         >=
#         #                         - M * (2 - model.b[p, c, s, d] - model.a[v, c, i, s, d])
#         #                         )

#         # model.pprint()
#         # # 2nd constraint
#         # model.path_cons = ConstraintList()
#         # for c in model.C:
#         #     for sd in chains[c].users:
#         #         s = sd[0]
#         #         d = sd[1]
#         #         model.path_cons.add(sum([model.b[s, d, p, c] for p in model.K_sd]) == 1)
#         opt = SolverFactory("cplex", executable="/opt/ibm/ILOG/CPLEX_Studio_Community128/cplex/bin/x86-64_linux/cplex")
#         # opt.options["threads"] = 4
#         results = opt.solve(model)
#         # model.pprint()
#         node_cap = []
#         tmp_1 = 0
#         tmp_2 = 0
#         theta = {}
#         # model.x.pprint()
#         for v in model.V:
#             # node_cap.append(value(model.x[v]))
#             for c in model.C:
#                 for (s, d) in model.R[c]:
#                     for p in model.p:
#                         for i in model.nc[c]:
#                             # print(value(model.a[v, c, i, s, d]))
#                             tmp_1 += value(model.a[v, c, p, i, s, d])
#                             tmp_2 += value(model.a[v, c, p, i, s, d])
#                     theta[(c, s, d, v)] = tmp_2
#                     tmp_2 = 0
#             node_cap.append(tmp_1)
#             tmp_1 = 0
#         # model.a.pprint()
#         # model.b.pprint()
#         # model.path_selection_cons.pprint()
#         # model.balance_cons.pprint()
#         # model.seq_cons.pprint()
#         # model.b.pprint()
#         # model.a.pprint()
#         # print(I)
#         # print(k_path[("1", "2")])
#         # print(node_cap)
#         # print(results)
#         # model.b.pprint()
#         plt.bar(graph.node_name_list, node_cap)
#         plt.show()
#         print(results)
#         print("node capcity in pricing:", node_cap)
#         # plt.savefig('result.pdf')
#         return theta
#         # return 1
#         # self.pattern_generator(model)
#         # # model.satisfy_req_1_cons.pprint()
#         # print(model.balancke_cons)

#     # def pattern_generator(self, model):
#     #     p ={}
#     #     for v in model.V:
#     #         tmp = sum

#     def __master(self, patter_num, theta, graph, functions, chains, k_path):
#         node_num = len(graph.node_list)
#         func_num = len(functions)
#         chain_num = len(chains)
#         sou_num = node_num
#         dist_num = node_num
#         M = 100000
#         # K_path_num = 2
#         # chain_num = 3
#         # source_distinations = [
#         #     [(1, 1), (2, 14), (3, 13)], 
#         #     [(1, 1), (2, 14), (3, 13)],
#         #     [(1, 1), (2, 14), (3, 13)],
#         # ]
#         # k_path = {
#         #     (1, 1): [(1, 2, 1), (1, 3, 1)],
#         #     (2, 14): [(2, 3, 5, 14), (2, 3, 6, 14)],
#         #     (3, 13): [(3, 4, 5, 13), (3, 4, 6, 13)]
#         # }

#         ##########################################
#         # Define concrete model
#         ###########################################
#         model = ConcreteModel()

#         ###########################################
#         # Sets
#         ###########################################

#         # Set of nodes: v
#         model.V = graph.node_name_list
#         # Set of functions: F
#         model.F = range(func_num)
#         # Set of chains: C
#         model.C = range(chain_num)
#         # Set of sources: S
#         model.S = []
#         for c in range(chain_num):
#             for i in range(len(chains[c].users)):
#                 model.S.append(chains[c].users[i][0])
#         # model.S = graph.node_name_list
#         # Set of distinations: D
#         model.D = []
#         for c in range(chain_num):
#             for i in range(len(chains[c].users)):
#                 model.D.append(chains[c].users[i][1])
#         # model.D = graph.node_name_list
#         # Set of K shortest paths: K_sd
#         model.k_path = k_path
#         # Set of k paths
#         model.p = range(patter_num + 1)
#         # Set of function of each chain
#         nc = []
#         model.nc = []
#         for c in range(chain_num):
#             nc.append(len(chains[c].fun))
#             tmp = range(len(chains[c].fun))
#             model.nc.append(tmp)
#         model.nf = []
#         for f in functions.keys():
#             model.nf.append(functions[f])
#         # model.nf = nf
#         # model.i(C) = 
#         # Set of users
#         model.R = []
#         for c in range(chain_num):
#             model.R.append(chains[c].users)
#             # Nodes capacity
#         model.n = graph.node_list[0].cap
#         # Set of IDs
#         model.I = {}
#         I = {}
#         for c in range(chain_num):
#             for f_num, f_name in enumerate(functions.keys()):
#                 for i in range(nc[c]):
#                     if chains[c].fun[i] == f_name:
#                         I[(f_num, i, c)] = 1
#                         model.I[(f_num, i, c)] = 1
#                     else:
#                         I[(f_num, i, c)] = 0
#                         model.I[(f_num, i, c)] = 0

#         # print(theta)
#         for v in model.V:
#             for c in model.C:
#                 for (s, d) in model.R[c]:
#                     # print(value(model.a[v, c, i, s, d]))
#                     self.theta[(patter_num, c, s, d, v)] = theta[(c, s, d, v)]
#         model.theta = self.theta
#         # print(model.I)
#         ###########################################
#         # Variables
#         ###########################################
#         model.t = Var(within=NonNegativeReals)
#         # model.a = Var(model.V, model.C, model.F, model.S, model.D, within= Binary)
#         # model.a = Var(model.V, model.C, model.nc[0], model.S, model.D, within= Binary)
#         model.b = Var(model.p, model.C, model.S, model.D, within=NonNegativeReals)
#         # model.d = [] * 4
#         # for c in model.C:
#         # model.d = Var(model.nc[0], model.C, model.S, model.D, within= Binary)
#         ###########################################
#         # Objective function: min. t
#         ###########################################
#         model.obj = Objective(expr=model.t, sense=minimize)

#         ###########################################
#         # Constraints
#         ##########################################
#         # 1st constraint
#         model.tmp = 10
#         model.balance_cons = ConstraintList()
#         for v in model.V:
#             model.balance_cons.add(sum([model.theta[(p, c, s, d, v)] *
#                                         model.b[(p, c, s, d)]

#                                         for c in model.C
#                                         for s, d in model.R[c]
#                                         for p in model.p
#                                         ])
#                                    <=
#                                    model.t
#                                    )
#         model.path_selection_cons = ConstraintList()
#         for c in model.C:
#             for (s, d) in model.R[c]:
#                 model.path_selection_cons.add(sum([model.b[p, c, s, d]
#                                                    for p in model.p
#                                                    ])
#                                               ==
#                                               1
#                                               )
#         print('%%%%%%%%%%%')
#         # model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
#         model.dual = Suffix(direction=Suffix.IMPORT)
#         opt = SolverFactory("cplex", executable="/opt/ibm/ILOG/CPLEX_Studio_Community128/cplex/bin/x86-64_linux/cplex")
#         model.b.pprint()
#         # "cplex", executable="/opt/ibm/ILOG/CPLEX_Studio_Community128/cplex/bin/x86-64_linux/cplex"
#         # opt.options["threads"] = 4
#         results = opt.solve(model)
#         # model.balance_cons.pprint()
#         # print(results)
#         # model.b.pprint()
#         dual = []
#         # print('dual')
#         # for c in model.component_objects(pyo.Constraint, active=True):
#         # print("constraint", c)
#         model.dual.pprint()
#         for index in model.balance_cons:
#             dual.append(model.dual[model.balance_cons[index]])
#         # model.dual.display()
#         node_cap = []
#         for v in model.V:
#             node_cap.append(sum([value(model.theta[p, c, s, d, v]) *
#                                  round(value(model.b[(p, c, s, d)]))

#                                  for c in model.C
#                                  for s, d in model.R[c]
#                                  for p in model.p
#                                  ]))
#         print(node_cap)
#         # plt.bar(graph.node_name_list, node_cap)
#         # plt.show()
#         # plt.savefig('result1.pdf')
#         # print(dual)
#         # model.balance_cons.pprint()
#         return dual, node_cap
# ############################################################################
# # from pyomo.environ import *
# # from coopr.pyomo import *
# # warehouses_num = 3 
# # customers_num = 4
# # P = 2
# # d = {(0, 0): 1.7, (0, 1): 7.2, (0, 2): 9.0, (0, 3): 8.3,
# #      (1, 0): 2.9, (1, 1): 6.3, (1, 2): 9.8, (1, 3): 0.7,
# #      (2, 0): 4.5, (2, 1): 4.8, (2, 2): 4.2, (2, 3): 9.3}
# # model = ConcreteModel()
# # model.Locations = range(warehouses_num)
# # model.Customers = range(customers_num)
# # model.x = Var(model.Locations, model.Customers, bounds=(0.0, 1.0))
# # model.y = Var(model.Locations, within=Binary)
# # model.obj = Objective( expr = sum([d[n,m] * model.x[n, m] for n in model.Locations for m in model.Customers])) 
# # model.single_x = ConstraintList()
# # for m in model.Customers:
# #     model.single_x.add(
# #         sum([model.x[n, m] for n in model.Locations]) == 1.0
# #     ) 
# # model.bound_y = ConstraintList()
# # for n in model.Locations:
# #     for m in model.Customers:
# #         model.bound_y.add(model.x[n, m] <= model.y[n])
# # model.num_facilities = Constraint(
# #     expr = sum([model.y[n] for n in model.Locations]) == P
# # ) 
# # opt = SolverFactory("glpk")
# # results = opt.solve(model)                             
# # model.pprint()
# # results.write()
# # model = ConcreteModel()
# # model.x_1 = Var(within=Binary)
# # model.x_2 = Var(within=Binary)
# # model.obj = Objective(expr=model.x_1, sense=minimize)
# # model.con1 = Constraint(expr=model.x_1  >= 0.5)
# # model.con2 = Constraint(expr=2*model.x_1 + 5*model.x_2 >= 2)
# # model.pprint()
# # opt = SolverFactory("glpk")
# # results = opt.solve(model)
# # results.write()