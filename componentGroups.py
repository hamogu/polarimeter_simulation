import numpy as np
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import axes3d
from astropy.table import Table, Column, vstack
from transforms3d.euler import euler2mat

from marxs.source.labSource import FarLabPointSource, LabPointSource, LabPointSourceCone
from marxs.optics.baffle import Baffle
from marxs.optics.multiLayerMirror import MultiLayerMirror
from marxs.optics.grating import FlatGrating
from marxs.optics.detector import FlatDetector
from marxs.optics.polarization import polarization_vectors

from energyDistributions import createEnergyTable




class SourceMLMirror():
	#this will also alllow the elements to wiggle later. RN it goes light source --> MLMirror
	# The mirror is at the center of this object


	def __init__(self, reflFile, testedPolarization, openningAngle, sourceDistance = 500, **kwargs):
		'''Default Setup:
		Z+ is out of the screen. X+ is to the right. Y+ is upwards.

		   Source
		   	|
		   	|
		   	|
		   	MLMirror------>
		'''
        # parameters for coneSource -- THESE WILL ALL BE WOBBLED LATER
		self.sourcePos = [0, sourceDistance , 0]
		self.sourceDirection = [0,-1,0]
		self.delta = openningAngle/2 

		#mirrorData Defaults
		self.reflFile = reflFile
		self.testedPolarization = testedPolarization

		self.defaultMirrorOrientation = euler2mat(-np.pi/4, 0, 0, 'syxz')
		self.defaultMirrorOrientation = np.dot(euler2mat(0,-np.pi/2,0,'syxz'),self.defaultMirrorOrientation)

		self.defaultMirrorPosition = np.array([0,0,0])
		
		#INITAL DEFAULTS
		self.currentMirrorOrientation = self.defaultMirrorOrientation
		self.currentMirrorPosition = self.defaultMirrorPosition

		# Generate Mirror
		self.mirror = MultiLayerMirror(self.reflFile, self.testedPolarization,
        position=self.currentMirrorPosition, orientation=self.currentMirrorOrientation)

	def updateMirror(self):
		# Generate Mirror
		self.mirror = MultiLayerMirror(self.reflFile, self.testedPolarization,
        position=self.currentMirrorPosition, orientation=self.currentMirrorOrientation)


	def __str__(self):
		report = "CURRENT SETUP\n"

		report += "Mirror:\n" 

		report += "    -center: " + str(self.mirror.geometry['center']) + "\n"
		report += "    -norm: "+ str(self.mirror.geometry['plane']) + "\n"
		
		report += " \n \n"
		report += "Source:\n"
		report += "    -position: " + str(self.sourcePos)+ "\n"
		report += "    -direction: " + str(self.sourceDirection)+ "\n"
		report += "    -solid angle: " + str(self.delta) + " steradians"+ "\n"

		report += "\n \n RAW: \n"
		report += str(self.mirror.geometry)

		return report
			

	def generate_photons(self, exposureTime, flux=100, V=10, I=0.1):

		# Generate Initial Photons

		energies = createEnergyTable('C', V_kV = V, I_mA = I) 

		source = LabPointSourceCone(self.sourcePos, delta = self.delta, energy= energies, direction = self.sourceDirection, flux = flux) # Generate photons from original source
		photons = source.generate_photons(exposureTime)


		reflectedPhotons = self.mirror.process_photons(photons)



		# Removing photons with zero probability
		rowsToRemove = []
		for i in range(0,len(photons)):
			if (photons[i]['probability']==0):
				rowsToRemove.append(i)

		rowsToRemove = np.array(rowsToRemove)
		photons.remove_rows(rowsToRemove)

		return reflectedPhotons

	def offset_mirror_orientation(self, rotationMatrix):
		# This is used to rotate the mirror relative to its default orientation

		# Update Mirror Orientation
		rotationMatrix = np.array(rotationMatrix)
		self.currentMirrorOrientation = np.dot(rotationMatrix, self.defaultMirrorOrientation)

		# Reset Mirror Position
		self.currentMirrorPosition = self.defaultMirrorPosition

		self.updateMirror()

	def offset_mirror_position(self, position):
		# This is used to place the mirror relative to its default position

		# Reset Mirror Orientation
		self.currentMirrorOrientation = self.defaultMirrorOrientation

		# Update Mirror Position
		position = np.array(position)
		self.currentMirrorPosition = position

		self.updateMirror()
		

	def move_mirror_orientation(self,rotationMatrix):

		# Update Mirror Orientation
		self.currentMirrorOrientation = np.dot(rotationMatrix, self.currentMirrorOrientation)

		self.updateMirror()

	def move_mirror_position(self, displacement):
		# This is used to move the mirror relative to its current position

		self.currentMirrorPosition = self.currentMirrorPosition + np.array(displacement)

		self.updateMirror()









