# Comparing Cooperation and Competition Using Stakeholder Search
This is a a senior project for COMP 5690 at Mount Royal University, created in Winter 2022 by Olga Koldachenko, under the supervision of Dr. Alan Fedoruk.

## Abstract
A stakeholder search framework was used to solve a randomly generated traveling salesman problem, where cooperative agents incorporated the data of other agents performing the search, while competitive agents iterated only on their own solutions. All agents ran the same genetic algorithm, with varying fitness functions to illustrate different goals. Cooperative agents performed significantly better than competitive agents in all cases. Another comparison was made for selfish agents, who share the solution best for their own fitness function, and selfless agents, who share the solution based on the chair’s, with better results from selfish agents, which share more diverse solutions. 

While cooperation gives better results overall, there’s also a reduction in genetic diversity, which is compounded by selflessness and its accompanying reduction in the individuality of the solutions shared by the stakeholders. In the future, it would be worth exploring the benefits of a more diverse pool of stakeholders, including variations in the genetic algorithm being run and variations in the algorithm overall, instead replacing it with other forms of artificial intelligence like tree-based search or neural networks.    

## Dependencies
- pygad
- numpy
- pandas
- matplotlib

## How To Run
The parameter given to stake.py is the name of one of the configuration files found in the server_configs directory, without the .csv extension. If no argument is given, then it will run a TSP of size 20 by default.