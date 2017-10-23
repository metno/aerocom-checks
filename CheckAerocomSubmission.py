#!/usr/bin/env python3

#Copyright (C) 2017 met.no
#Contact information:
#Norwegian Meteorological Institute
#Box 43 Blindern
#0313 OSLO
#NORWAY
#E-mail: jan.griesfeller@met.no
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#MA 02110-1301, USA

################################################################
import pdb
import argparse
import sys
import os
import re

################################################################
def GetFileList(ExperimentName='CTRL2016', Model='*', ReturnExperimentsFlag=False, VerboseFlag=False):
	"""returns the file list for a given model experiment
	in form so that it can be directly tested via glob"""
	
	import configparser
	#reserved names
	#note that configparser converts everything to lower case
	NotVarNames=['years','timestepstrings','datatypes']
	#Read Ini file constants.ini
	ConfigIni=os.path.join(os.path.dirname(os.path.realpath(__file__)),'constants.ini')
	IniFileData=configparser.ConfigParser()
	IniFileData.read(ConfigIni)
	#pdb.set_trace()
	if ReturnExperimentsFlag is True:
		return ','.join(sorted(IniFileData.sections()))

	if IniFileData.has_section(ExperimentName):
		Years=IniFileData[ExperimentName]['Years'].split(',')
		TSStrings=IniFileData[ExperimentName]['TimeStepStrings'].split(',')
		DataTypes=IniFileData[ExperimentName]['DataTypes'].split(',')
		Vars=IniFileData.options(ExperimentName)
		Files=[]
		#special programming for certain experiments; stnadrd list all combinations
		if ExperimentName == 'Remote.Sensing':
			pattern=re.compile('.*3d$')
			for Var in sorted(Vars):
				if Var in NotVarNames:
					continue
				for TSString in TSStrings:
					for Year in Years:
						if pattern.match(Var):
							#the 3d vars should be provided only for year 2010
							if Year != '2010':
								continue
						for DataType in IniFileData[ExperimentName][Var].split(','):
							Filename='_'.join([Model,Var,DataType,Year,TSString])+'.nc'
							Files.append(Filename)
		#elif ExperimentName == 'Remote.Sensing':
		else:
			#standard: list combinations of the Years, Time step strings and data types	
			#put together the file names
			for Var in sorted(Vars):
				if Var in NotVarNames:
					continue
				for TSString in TSStrings:
					for Year in Years:
						for DataType in IniFileData[ExperimentName][Var].split(','):
							Filename='_'.join([Model,Var,DataType,Year,TSString])+'.nc'
							Files.append(Filename)


		return Files


################################################################
def CheckModelDir(ModelDir, FileList, VerboseFlag=False):
	"""check model directory for necessary files
	
	the directory will be searched recursively, so be aware of 
	big directory structures
	the files are assumed to end with '.nc'
	"""
	import glob
	import itertools

	MatchingFiles=[]
	MissedFiles=[]

	#AllFiles=glob.glob(ModelDir+"/**/*.nc", recursive=True)

	for File in FileList:
		MatchFiles=glob.glob(os.path.join(ModelDir+'/**/',File))
		if len(MatchFiles) >=1:
			MatchingFiles.append(MatchFiles)
		else:
			MissedFiles.append(File)

	#the following is needed since FoundFiles can be a list of lists
	#when the file search finds more than one file matching the criterion
	#it flattens the list of lists to a 1 dimensional list
	MatchingFiles=list(itertools.chain.from_iterable(MatchingFiles))
	
	return MissedFiles, MatchingFiles


################################################################


if __name__ == '__main__':
	Experiments=GetFileList('',ReturnExperimentsFlag=True)

	parser = argparse.ArgumentParser(description='Program to check if a model directory contains the right data files to participate in a certain aerocom model experiment.')
	parser.add_argument("experiment", help="experiment name; supported are "+Experiments)
	parser.add_argument("--modeldir", help="model directory to check; defaults to '.'",default='.')
	parser.add_argument("--listfiles", help="print file list only",action='store_true')
	parser.add_argument("-v","--verbose", help="be verbose",action='store_true')

	args = parser.parse_args()

	if args.experiment:
		Experiment=args.experiment
	if args.modeldir:
		ModelDir=args.modeldir
	if args.listfiles:
		ListFlag= args.listfiles
	else:
		ListFlag=False
	if args.verbose:
		VerboseFlag=args.verbose
	else:
		VerboseFlag=False

	Files=GetFileList(Experiment)
	if ListFlag is True:
		for File in sorted(Files):
			sys.stdout.write(File.replace('*','aerocom3_MODELNAME')+'\n')
		sys.exit(0)

	#pdb.set_trace()
	MissedFiles, MatchingFiles = CheckModelDir(ModelDir, Files, VerboseFlag=VerboseFlag)
	
	sys.stderr.write('missing files:\n')
	for File in sorted(MissedFiles):
		sys.stderr.write(File+'\n')
	
	if VerboseFlag is True:
		sys.stdout.write('found files in '+os.path.dirname(MatchingFiles[0])+':\n')
		for MatchFile in sorted(MatchingFiles):
			sys.stdout.write(os.path.basename(MatchFile)+'\n')

