import streamlit as st
import copy
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from pickle import dump
from pickle import load
import math
import ezdxf
from shapely.geometry import Polygon, LineString, Point
import re
import random

st. set_page_config(layout="wide")

st.sidebar.image('logo-png.png',use_column_width=True)

ver=st.__version__
ver = int(ver.replace('.', "")[:3])

if ver >= 128:
	SupportColor = True
else:
	SupportColor = False

if 'md' not in st.session_state:
	st.session_state.md = os.getcwd()

if 'tool' not in st.session_state:
	st.session_state.tool = 'Create Model'

ToolSync = 1 # Space if statement just to keep indent same at full tool
if ToolSync ==1:

	# All session state initiated
		
	if 'PageOption2' not in st.session_state:
		st.session_state.PageOption2 = 1
			
	def PageOption2call():
		if st.session_state.PageOption2key:
			st.session_state.PageOption2 = PageOptions2.index(st.session_state.PageOption2key)	
	if 'generate' not in st.session_state:
		st.session_state.generate = False

	if 'basesuff' not in st.session_state:
		st.session_state.basesuff = ""
		
	if 'propsuff' not in st.session_state:
		st.session_state.propsuff = ""	


	if st.session_state.tool == 'Create Model':
		if 'wd01' not in st.session_state:
			st.session_state.wd01 = ""
		wd01 = st.sidebar.text_input('Input Project Name/Folder', st.session_state.wd01)
		st.session_state.wd01 = wd01[:]
		
		cwd = str(st.session_state.md)+'/Model-'+str(wd01)+'/'
		
		if not os.path.isdir(cwd) and wd01 != "":
			if st.sidebar.button('Create Working Directory'):
				#os.chdir(str(st.session_state.md))
				if wd01 != '':
					try:
						os.mkdir(str(st.session_state.md)+'/Model-'+str(wd01))
					except:
						pass


		if wd01 != "" and os.path.isdir(cwd):
		
			SimTool = st.sidebar.radio("Simulation Tool:", ('EnergyPlus', 'eQUEST'), index=0)
			
			Heading = "Create " + str(SimTool) + " Model for: " + str(wd01)
			font_size = 30

			html_str = f"""
			<style>
			p.a {{
			  font: bold {font_size}px Courier;
			  color: purple;
			}}
			</style>
			<p class="a">{Heading}</p>
			"""
			
			st.markdown(html_str, unsafe_allow_html=True)
		
		
			with st.expander ("Instructions"):
				if SupportColor:
					st.markdown(''':green[*1) All shells / floors for the model should be created on a different layer in the dwg file.\n2) Only vertical & rectangular windows are currently supported. All windows are currently defined as a slanting line from lower left to upper right. The windows can be traced over the elevation plans and then it needs to be superimposed over the zoning diagram in dwg.\n3) Each layer should consist of zoning lines and windows lines only.\n4) The file needs to be saved in DXF format only.\n5) This tool currently works only with lines and not polylines or shapes.\n\n Recommendations:\n1) Other than the default layers, the dxf should contain only the layers containing zoning diagram. There is an option to select layers for the model and can work if there are more layers too but will need to be deselected from the list in this tool.\n2) The tool has a lot of inbuilt checks and fetures to break lines, merge lines that do not intersect, remove duplicate lines, etc. However to eleminate chances of error, it is highly recommended to use all broken lines in the zoning diagram and make sure the endpoints of all lines coincide with endpoints of some other line.\n3) Watching video demonstration or attending an online meet will simplify things a lot. Adding windows in dxf may seem tricky and may take similar amount of time as doing in eQUEST and EnergyPlus but it is very helpful because we do not need to create them again if we need to change the internal zoing in the model.\n\nPlanned Future Development:\n1) Allow use of polylines.\n2) Support using rectangles for windows instead of slanting lines, though it does not add much benefit other than aesthetics of dxf.\n3) Add ceiling and floor heights in the dxf itself rather than tool.\n4) Support non rectangular window input.\n\nFor any questions, contact:\nSrijan Didwania (srijandidwania@syngineers.in)*]''')
				else:
					st.markdown("1) All shells / floors for the model should be created on a different layer in the dwg file.\n2) Only vertical & rectangular windows are currently supported. All windows are currently defined as a slanting line from lower left to upper right. The windows can be traced over the elevation plans and then it needs to be superimposed over the zoning diagram in dwg.\n3) Each layer should consist of zoning lines and windows lines only.\n4) The file needs to be saved in DXF format only.\n5) This tool currently works only with lines and not polylines or shapes.\n\n Recommendations:\n1) Other than the default layers, the dxf should contain only the layers containing zoning diagram. There is an option to select layers for the model and can work if there are more layers too but will need to be deselected from the list in this tool.\n2) The tool has a lot of inbuilt checks and fetures to break lines, merge lines that do not intersect, remove duplicate lines, etc. However to eleminate chances of error, it is highly recommended to use all broken lines in the zoning diagram and make sure the endpoints of all lines coincide with endpoints of some other line.\n3) Watching video demonstration or attending an online meet will simplify things a lot. Adding windows in dxf may seem tricky and may take similar amount of time as doing in eQUEST and EnergyPlus but it is very helpful because we do not need to create them again if we need to change the internal zoing in the model.\n\nPlanned Future Development:\n1) Allow use of polylines.\n2) Support using rectangles for windows instead of slanting lines, though it does not add much benefit other than aesthetics of dxf.\n3) Add ceiling and floor heights in the dxf itself rather than tool.\n4) Support non rectangular window input.\n\nFor any questions, contact:\nSrijan Didwania (srijandidwania@syngineers.in)")
			
			
			if SimTool == 'EnergyPlus':
				#cwd = cwd+'Model/'
				if not os.path.isdir(cwd) and wd01 != "":
					try:
						os.mkdir(str(st.session_state.md)+'/Model-'+str(wd01))
					except:
						pass
						
				st.markdown("Proposed and Baseline Modeling")
				
				
				with st.expander ("Building Details and Geometry"):
					generatebutton = False
					
					uploadcols = st.columns([5,0.2,1.7,3])
					
					dxf = uploadcols[0].file_uploader("Upload DXF file", type = ['dxf'])
					
					if dxf is not None:
						
						uploadcols[2].text("")
						uploadcols[2].text("")
						uploadcols[3].text("")
						uploadcols[3].text("")
						if uploadcols[2].checkbox("Use WWR?", value = False):
							WWRmethod = True
						else:
							WWRmethod = False
							
						if uploadcols[2].checkbox("Plenum per Zone?", value = False):
							PlnmPerZone = True
						else:
							PlnmPerZone = False
							
						if uploadcols[2].checkbox("Is it re-zoning?"):
							redo = True
						else:
							redo = False
						
						if uploadcols[3].checkbox("Diagnostic Mode for Geometry?", value = False):
							Diagnostic = True
						else:
							Diagnostic = False

						if uploadcols[3].checkbox("Do Not Merge Close Coordinates?", value = False):
							MergeCloseCoor = False
						else:
							MergeCloseCoor = True
							
						if uploadcols[3].checkbox("DXF File has Lines for Ceiling and Floor Height?", value = False):
							CeilFlrInCAD = True
						else:
							CeilFlrInCAD = False
	
						if SupportColor:
							st.markdown(''':red[*Recommendation - Keeping plan orientation in DXF helps with debugging. Change azimuth in simulation tool.*]''')
						else:
							st.markdown("Recommendation - Keeping plan orientation in DXF helps with debugging. Change azimuth in simulation tool.")
						
						generatebutton = True
						with open(os.path.join(cwd,dxf.name),"wb") as f:
							f.write(dxf.getbuffer())
						
						# If Diagnostic Mode Not On
						StartFlr = 0
						BreakAfterFlr = 100
						MergeCloseCoor = True
						DoOnlyOneFlrLayer = False
						
						# if Diagnostic Mode On						
						if Diagnostic:
							st.text("")
							st.text("To generate limited floors for diagnostic purposes:")
							DXFCols = st.columns([2,2,2])
							StartFlr = int(DXFCols[0].text_input('Starting Floor',0))
							DXFCols[0].text(">If doing a single flr as diagnostic use Flr number starting from 0 else use 0.")
							BreakAfterFlr = int(DXFCols[1].text_input('Upto Floor',100))
							DXFCols[1].text("> put any large value to complete all flrs. start from flr 0.")
							
							DXFCols[2].text("")
							DXFCols[2].text("")
							if DXFCols[2].checkbox("Stop after zoning one floor?", value = False):
								DoOnlyOneFlrLayer = True
							else:
								DoOnlyOneFlrLayer = False
							
						
							
							
						if WWRmethod:
							WWRcols = st.columns([8,8,8,8,8,8,8,8])
							wwrn = float(WWRcols[0].text_input('N WWR',0.2))
							wwrne = float(WWRcols[1].text_input('NE WWR',0.2))
							wwre = float(WWRcols[2].text_input('E WWR',0.2))
							wwrse = float(WWRcols[3].text_input('SE WWR',0.2))
							wwrs = float(WWRcols[4].text_input('S WWR',0.2))
							wwrsw = float(WWRcols[5].text_input('SW WWR',0.2))
							wwrw = float(WWRcols[6].text_input('W WWR',0.2))
							wwrnw = float(WWRcols[7].text_input('NW WWR',0.2))
							
						
						DXFFile = str(cwd+dxf.name)
						doc = ezdxf.readfile(DXFFile)
						msp = doc.modelspace()
						lines = msp.query('LINE[layer=="F1"]') # this layer filtering is currently not used as this lines variable is not used in this code

						def print_entity(e):
							print("LINE on layer: %s\n" % e.dxf.layer)
							print("start point: %s\n" % e.dxf.start)
							print("end point: %s\n" % e.dxf.end)
							
							
						def length(A,B):
							return ((B[1]-A[1])**2 + (B[0]-A[0])**2 + (B[2]-A[2])**2)**0.5

						def lengthXY(A,B):
							return ((B[1]-A[1])**2 + (B[0]-A[0])**2)**0.5

						
						# Get Layer List

						LayerList = []
						for e in msp.query("LINE"):
							LayerList.append(e.dxf.layer)

						LayerList = list(set(LayerList))
						LayerList.sort()	
						
						st.text("")
						st.text("")
						
						LayersCols = st.columns([2,2])
						
						LayerListInput = LayersCols[0].text_input('Adjust Shell Layer Names in order from bottom to top if not in order', ",".join([str(elem1) for elem1 in LayerList]))
						LayerList = LayerListInput.split(",")
						LayerList = [str(i) for i in LayerList]
						
						GroundLayers = LayersCols[1].text_input('Floor layers with Ground exposure:', LayerList[0])
						GroundLayerList = GroundLayers.split(",")
						
						NumberOfFlrs = len(LayerList)
						st.text("Number of Shells / Floors being modeled = " + str(NumberOfFlrs))
						st.text("")
						st.text("")

						Adjacency = st.columns([2,2])
						
						
						def ft_to_m(x):
							return round(x*0.3048,5)
						
						if not CeilFlrInCAD:
						
							initialCeilHt = [9]*len(LayerList)
							initialFlrHt = [12]*len(LayerList)
							
							CeilingHts = Adjacency[0].text_input('Enter Ceiling Ht for each Floor separated by comma from bottom to up', str(','.join([str(x) for x in initialCeilHt])))
							if CeilingHts != "":
								CeilingHtList_Ft = CeilingHts.split(",")

								CeilingHtList_Ft = [float(i) for i in CeilingHtList_Ft]
								
								CeilingHtList = [ft_to_m(element) for element in CeilingHtList_Ft]
							
							FloorHts = Adjacency[1].text_input('Enter Plnm Ht for each Floor separated by comma from bottom to up', str(','.join([str(x) for x in initialFlrHt])))
							
							if FloorHts != "":
								FloorHtList_Ft = FloorHts.split(",")
								FloorHtList_Ft = [float(i) for i in FloorHtList_Ft]
								
								FloorHtList = [ft_to_m(element) for element in FloorHtList_Ft]
								
							if len(FloorHtList) == len(CeilingHtList) and CeilingHts != "" and FloorHts != "":
								
								PlnmHtList = [FloorHtList[i]-CeilingHtList[i] for i in range(len(CeilingHtList))]
							else:
								generatebutton = False
						
						st.text("")
						st.text("")		
						EnergyPlusVer = st.selectbox('EnergyPlus Version:',['8.9', '9.1', '9.6'], index=2)
						
						if EnergyPlusVer == "8.9":
							SketchupV89 = True
						else:
							SketchupV89 = False
							
						if EnergyPlusVer != '9.6':
							st.text("*This generator currently writes a Spc Name keyword for Buiding Surfaces as required for EP > 9.6. Will need to remove that line from idf.")
					
					
					st.text("")	
					if generatebutton:		
						if st.button('Generate Model'):
							with st.spinner('Generating Enery Plus Model and related documents........'):
								
							
								st.session_state.generate = True
								with open(str(cwd)+"logs.txt", "w") as log_file:
									NumberOfFlrs = len(LayerList)
									log_file.write("\n" + str(NumberOfFlrs) +" Floors")

									# To have Linelist and NewLineList for each floor saved
									LineListDict = {}
									NewLineListDict = {}
									SpcCoorListDict = {}
									SpcDictDict = {}
									FlrLayerDict = {}
									# Start code for each layer
									
									
									if EnergyPlusVer == "8.9":
										#suffix = "_IDF_sk89.idf"
										with open('EPlusIDF8-9.idf', 'r') as f:
											InitialIDF = f.readlines()
									elif EnergyPlusVer == "9.1":
										#suffix = "_IDF_9-1_Fenes.idf"
										with open('EPlusIDF9-1.idf', 'r') as f:
											InitialIDF = f.readlines()
									else:
										with open('EPlusIDF9-6.idf', 'r') as f:
											InitialIDF = f.readlines()



									with open(str(cwd)+"Geometry.idf", "w") as text_file:
									#ExtListDict = {} (currently not implementing automatic logic for intermediate roof flrs)
									#FloorCDict = {} (currently not implementing automatic logic for intermediate roof flrs)
										

										text_file.writelines(InitialIDF)

										text_file.write('\n\nGlobalGeometryRules,\n')
										text_file.write('    LowerLeftCorner,         !- Starting Vertex Position\n')
										text_file.write('    CounterClockWise,        !- Vertex Entry Direction\n')
										text_file.write('    Relative;                !- Coordinate System\n\n')

										
										
					try:
						with open(str(cwd+'Geometry.idf'), 'r') as geomfiledwnld:
							st.download_button(
								 label="Download Geometry File",
								 data = geomfiledwnld,
								 file_name=str("Geometry.idf"),
								 mime='text/csv',
							 )
						 
					except:
						pass
