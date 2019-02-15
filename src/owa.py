#! /usr/bin/python


def owa_weights(max_rank):
	Delta = 8
	m=Delta
	weights=[0]*(m+1)
	#beta=1-0.001 #1.0/Delta - 0.001
	beta=1.0/Delta - 0.001
	f_i = [1]*(m+1)
	#f_i = [1./Delta*x for x in range(1,m+1)]
	rescale=10000
	weights[1] = rescale*f_i[0]*beta**(m-1)/(1+beta)**(m-1)
	weights[2:] = [rescale*f_i[x-1]*beta**(m-x)/(1+beta)**(m+1-x) for x in range(2,m+1)]	
	weights[0] = max(weights[1:])+1
	#print weights
	if max_rank>Delta:
		for Delta in range(Delta,max_rank):
			#print Delta
			weights.append(weights[0])
	
	print(["%0.5f" % x for x in weights])
	return weights
##
##weights=owa_weights(8)
##
##
##v_1=[1,2,2,3,4,5,5,6,7,8]
##v_2=[1,2,2,3,4,4,5,6,7,8]
##
##sv_1=sum([weights[x+1]*v_1[x]/8 for x in range(1,10)])
##sv_2=sum([weights[x+1]*v_2[x]/8 for x in range(1,10)])
##
##print sv_1
##print sv_2
##
##
####Example from Yager 1997b:
##weights=[0]*5
##f_i=[1]*4
##f_i=[1,0.8,0.7,0.6]
##f_i=[1,0.9,0.8,0.6]
##f_i=[1,0.9,0.7,0.4]
##beta=0.01
##Delta=4
##weights[2:] = map(lambda x: f_i[x-1]*beta**(Delta-x)/(1+beta)**(Delta+1-x), range(2,Delta+1))
##weights[1] = f_i[0]*beta**(Delta-1)/(1+beta)**(Delta-1)
##print weights
##print reduce(lambda x,y: x+y,weights,0)
