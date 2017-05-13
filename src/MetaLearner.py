# Evolution Strategies for meta-learning

# lib
import numpy as np
from keras.models import model_from_json

# src
from .ESTrainer import ESTrainer


class MetaLearner :
	def __init__( self, model, env ) :
		self.env = env
		self.model = model_from_json( model.to_json( ) )  # deep copy
		self.model.set_weights( model.get_weights( ) )

	def Train( self, iterations=100, pop=100, lrStart=0.0003, sigmaStart=0.2,
			   popMeta=5, lrMeta=0.00001, sigmaMeta_lr=0.00001, sigmaMeta_sigma=0.01, render=False ) :
		lr = lrStart
		sigma = sigmaStart

		for i in range( iterations ) :
			metaParams = []

			while len( metaParams ) < popMeta :
				m = model_from_json( self.model.to_json( ) )  # deep copy
				m.set_weights( self.model.get_weights( ) )
				trainer = ESTrainer( m, self.env )
				lrNoise = np.random.normal( 0, sigmaMeta_lr )  # + noise
				sigmaNoise = np.random.normal( 0, sigmaMeta_sigma )  # + noise

				print( 'candidate -- lr: {}, sigma: {}'.format(lr+lrNoise, sigma+sigmaNoise))
				# test, append to metaParams
				reward = trainer.Train( iterations=5, population=pop, sigma=sigma + sigmaNoise, lr=lr + lrNoise,
										render=render )
				w = trainer.model.get_weights( )
				metaParams.append( [reward, lrNoise, sigmaNoise, w] )

			# do updates
			meanReward = sum( [x[0] for x in metaParams] ) / len( metaParams )  # to normalize
			bestReward = metaParams[0][0]
			bestW = metaParams[0][3]
			for meta in metaParams :
				if bestReward > meta[0] :
					bestReward = meta[0]
					bestW = meta[3]
				# weighted update of lr and sigma
				lr += (lrMeta / (sigmaMeta_lr * popMeta)) * (meta[0] - meanReward ) * meta[1]
				sigma += (lrMeta / (sigmaMeta_sigma * popMeta)) * (meta[0] - meanReward ) * meta[2]

			self.model.set_weights( bestW )

			print ("max reward is {}, lr is {}, sigma is {}".format( bestReward, lr, sigma ))
