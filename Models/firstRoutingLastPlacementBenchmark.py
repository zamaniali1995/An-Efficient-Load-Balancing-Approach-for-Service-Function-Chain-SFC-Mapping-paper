from coopr.pyomo import *
import  time
import InputConstants

class benchmark_first:
    def __init__(self):
        self.input_cons = InputConstants.Inputs()
    def run(self, graph, chains, function, alpha, user_num, batch_size, k, tune_param): 
        start_time = time.time()
        node_cpu_cap = []
        node_mem_cap = []
        batch_chain = []
        links_num = 0
        for c in chains.chains_list:
            for u in c.users:
                batch_chain.append([c, u, c.cpu_usage * c.tra, c.tra])
        batch_chain.sort(key=lambda x: x[2], reverse=True)
        batch_chain.sort(key=lambda x: x[3], reverse=True)
        for chain, u, _, _ in batch_chain:
            k_path = graph.k_path(u[0], u[1], k)
            path_num, link_num= self.__path_selection(graph, k_path, function, chain, alpha)
            links_num += link_num
            self.__node_selection(graph, chain, k_path[path_num], function, tune_param)
        for v in range(graph.nodes_num()):
            node_cpu_cap.append(graph.node_list[v].cons_cpu * 100)
            node_mem_cap.append(graph.node_list[v].cons_mem * 100)
        link_cap = []
        for l in range(len(graph.link_list)):
            link_cap.append(graph.link_list[l].cons * 100)
        end_time = time.time()
        print('heuristic full:', sum(node_cpu_cap))
        return max(node_cpu_cap), sum(node_cpu_cap)/len(node_cpu_cap), max(link_cap),\
        sum(node_cpu_cap)/len(node_cpu_cap), end_time - start_time, links_num
        
    def __path_selection(self, graph, k_path, function, c, alpha):
        path_cost =[]
        link_cons_list = []
        for k in k_path:
            for n in range(len(k) - 1):
                l = graph.name_to_num_link((k[n], k[n + 1]))
                link_cons_list.append(graph.link_list[l].cons)
            link_cons_avg = sum(link_cons_list) / (len(k) - 1)
            path_cost.append(link_cons_avg, len(k))
            link_cons_list = []
        path_cost.sort(key=lambda x: x[1], reverse=True)
        path_cost = [p[0] for p in path_cost]
        idx = path_cost.index(min(path_cost))
        for n in range(len(k_path[idx])-1):
            l = graph.name_to_num_link((k_path[idx][n], k_path[idx][n+1]))
            graph.link_list[l].cons += c.tra / graph.link_list[l].ban
        return idx, len(k_path[idx])-1

    def __node_selection(self, graph, c, path, functions, tune_param):
        req_cap = c.cpu_usage * c.tra / sum([graph.node_list[graph.name_to_num_node(v)].cap_cpu for v in path])
        node_cons = [graph.node_list[graph.name_to_num_node(v)].cons_cpu for v in path]
        max_cons = max(node_cons)
        min_cons = min(node_cons)
        res_cap = 0
        if max_cons == 0:
            divi_cap = (c.cpu_usage * c.tra) /sum([graph.node_list[graph.name_to_num_node(v)].cap_cpu for v in path])  
            divi_cap = divi_cap / len(path)
            i = 0
            v = 0
            if len(path) >= len(c.fun):
                for i in range(len(c.fun)):
                    graph.node_list[graph.name_to_num_node(path[v])].cons_cpu += functions.cpu_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_cpu
                    graph.node_list[graph.name_to_num_node(path[v])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_mem
                    v += 1
            else:
                tmp = divi_cap
                while( i < len(c.fun)):
                    if tmp + tune_param >=  functions.cpu_usage(c.fun[i]) * c.tra/graph.node_list[graph.name_to_num_node(path[v])].cap_cpu:
                        graph.node_list[graph.name_to_num_node(path[v])].cons_cpu += functions.cpu_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_cpu
                        graph.node_list[graph.name_to_num_node(path[v])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_mem
                        tmp -= functions.cpu_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_cpu
                        i += 1
                    elif v < len(path) - 1:
                        v += 1
                        tmp = divi_cap
                    elif i < len(c.fun):
                        for j in range(i, len(c.fun)):
                            graph.node_list[graph.name_to_num_node(path[v])].cons_cpu += functions.cpu_usage(c.fun[j]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_cpu
                            graph.node_list[graph.name_to_num_node(path[v])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_mem
                        i = len(c.fun)
        else:
            # min_index = node_cons.index(min(node_cons))
            # graph.node_list[graph.name_to_num_node(path[min_index])].cons_cpu += functions.cpu_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[min_index])].cap_cpu
            # graph.node_list[graph.name_to_num_node(path[min_index])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[min_index])].cap_mem

            # for v in path:
            #     res_cap += max_cons - graph.node_list[graph.name_to_num_node(v)].cons_cpu
            # ex_cap = (req_cap - res_cap) / len(path)
            # if ex_cap <0:
            #     ex_cap=0
            i = 1
            v = 1
            # tmp = ex_cap
            while( i <= len(c.fun)):
                # if tmp+(max_cons - graph.node_list[graph.name_to_num_node(path[v])].cons_cpu)+ tune_param >= (functions.cpu_usage(c.fun[i]) * c.tra)/graph.node_list[graph.name_to_num_node(path[v])].cap_cpu:
                    # graph.node_list[graph.name_to_num_node(path[v])].cons_cpu += functions.cpu_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_cpu
                    # graph.node_list[graph.name_to_num_node(path[v])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_mem
                if len(path)==v:
                    for j in range(i, len(c.fun)+1):
                        graph.node_list[graph.name_to_num_node(path[v])].cons_cpu += functions.cpu_usage(c.fun[j]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_cpu
                        graph.node_list[graph.name_to_num_node(path[v])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_mem
                
                min_index = node_cons.index(min(node_cons))
                graph.node_list[graph.name_to_num_node(path[min_index])].cons_cpu += functions.cpu_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[min_index])].cap_cpu
                graph.node_list[graph.name_to_num_node(path[min_index])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[min_index])].cap_mem
                node_cons = node_cons[min_index:]
                i += 1
                
             #   elif tmp+(max_cap - graph.node_list[graph.name_to_num_node(path[v])].cons_cpu) >=  functions.cpu_usage(c.fun[i]) * c.tra * tune_param:
              #      graph.node_list[graph.name_to_num_node(path[v])].cons_cpu += functions.cpu_usage(c.fun[i]) * c.tra / graph.node_list[v].cap_cpu
               #     graph.node_list[graph.name_to_num_node(path[v])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[v].cap_mem
                   # tmp -= functions.cpu_usage(c.fun[i]) * c.tra
                #    i += 1
                # elif v < len(path) - 1:
                #     v += 1
                #     tmp = ex_cap
                # elif i < len(c.fun):
                #     for j in range(i, len(c.fun)):
                #         graph.node_list[graph.name_to_num_node(path[v])].cons_cpu += functions.cpu_usage(c.fun[j]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_cpu
                #         graph.node_list[graph.name_to_num_node(path[v])].cons_mem += functions.mem_usage(c.fun[i]) * c.tra / graph.node_list[graph.name_to_num_node(path[v])].cap_mem
                #     i = len(c.fun)                       
