from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import folium
from folium import plugins
import os , sys
from PIL import Image, ExifTags
import webbrowser
 

mainWindow = Tk()
mainWindow.geometry('700x400')
mainWindow.title("PiloPlot")
try:
	mainWindow.iconbitmap('icon.ico')
except:
	pass

subHead = Label(mainWindow, text="The Picture Location Plotter", font=("Arial",14) )
mainHead = Label(mainWindow, text="PiloPlot", font=("Arial Bold",45) )
mainHead.pack()
subHead.pack()

lblFeautures = Label(mainWindow, text="The features you will have in your map",fg="grey", font=("Arial Bold",12))
lblFeautures.place(relx=0.5, rely=0.33, anchor=CENTER)

MT = Label(mainWindow, text="Measurement tools",font=("Arial Bold",12))
MT.place(relx=0.25, rely=0.39, anchor=CENTER)

Mini = Label(mainWindow, text="Minimap",font=("Arial Bold",12))
Mini.place(relx=0.50, rely=0.39, anchor=CENTER)

DT = Label(mainWindow, text="Drawing tools",font=("Arial Bold",12))
DT.place(relx=0.75, rely=0.39, anchor=CENTER)

m=folium.Map(location= [35.850516, 12.271080],zoom_start=10) 

measure = plugins.MeasureControl(position='topleft',active_color='red',completed_color='red',primary_length_unit='meters',secondary_length_unit='miles',secondary_area_unit='acres')
m.add_child(measure)

minimap = plugins.MiniMap(toggle_display=True, position='bottomright')
m.add_child(minimap)

drawingTool=plugins.Draw(export=True,position='topleft')
drawingTool.add_to(m)

var4 = IntVar()
CB = Checkbutton(mainWindow, text="Show an animated path connecting the locations", variable= var4,font=("Arial",12))
CB.place(relx=0.5, rely=0.53, anchor=CENTER)
 
plugins.Fullscreen(position='bottomleft').add_to(m)

def NoMap():
    messagebox.showinfo("Result","Did not get any geo-coordinates, hence map not generated!")
def ShowMap(count):
    ans = messagebox.askyesno("Result","Found "+str(count)+" images with geo-coordinates. Do you want to plot them on map?")
    if ans == True:
        m.save('./PiloPlotMap.html')
        webbrowser.open('PiloPlotMap.html')

def convToDegree(value):
	try:
		d=float(value[0])
		m=float(value[1])
		s=float(value[2])
		return d + (m/60.0) + (s/3600.0)
	except:
		d0=value[0][0]
		d1=value[0][1]
		dd = float(d0)/float(d1)

		m0=value[1][0]
		m1=value[1][1]
		mm = float(m0)/float(m1)
		
		s0=value[2][0]
		s1=value[2][1]
		ss = float(s0)/float(s1)
		return dd + (mm/60.0) + (ss/3600.0)

def back_task():
    
	folder_selected=filedialog.askdirectory()

	img_folder = str(folder_selected)
	img_contents = os.listdir(img_folder)#everything
	validCount=0
	antPath=[]
	for image in img_contents:
		full_path = os.path.join(img_folder,image)
		try:
			pil_img = Image.open(full_path)
			exif = {ExifTags.TAGS[k]: v for k, v in pil_img._getexif().items() if k in ExifTags.TAGS}
			locs= {}
			try:
				time1= exif['DateTimeOriginal'].split()
				Date = time1[0]
				Time = time1[1]
				width=250
				height=250
			except:
				print("Time not available!")
			try:
				for key in exif['GPSInfo'].keys():
					decVal= ExifTags.GPSTAGS.get(key)
					locs[decVal]=exif['GPSInfo'][key]
                
				lat_ref=locs.get('GPSLatitudeRef')
				long_ref=locs.get('GPSLongitudeRef')
				lati = locs.get('GPSLatitude')
				latDegree = convToDegree(lati)
				longi = locs.get('GPSLongitude')
				longDegree = convToDegree(longi)
            
				if lat_ref == "S":
					latDegree= -abs(latDegree)
				if long_ref == "W":
					longDegree= -abs(longDegree)
				print(latDegree,longDegree)

				validCount+=1
				add_latlong=[latDegree,longDegree]
				antPath.append(add_latlong)
				path=full_path
				path="file://"+path.replace('\\','/')
                
				htmlcode="""
				<h6> Image={file}<br> Taken Date(yyyy:mm:dd)= {date}<br> Taken Time(24hrs)= {time}</h6><br>
				<img src="{pic}" height={ht} width={wid} />
				""".format(pic=path,date=Date,time=Time,file=full_path,wid=width,ht=height)
                
                
				popup = folium.Popup(htmlcode, max_width=2650)
				icon = folium.Icon(color="red", icon="photo", prefix="fa")
				folium.Marker(add_latlong,popup=popup,tooltip=full_path,icon=icon).add_to(m)
                
			except:
				print("Image "+full_path+" has no GPS Info")
		except:
			print("NO EXIF FOUND for "+ full_path)

	try:
		m.location=[latDegree,longDegree]
		if var4.get()==1:
			plugins.AntPath(antPath).add_to(m)

		ShowMap(validCount)
        
	except:
		print("Map not generated!!")
		NoMap()

folderButton = Button(mainWindow, text="Select The Folder Containing Images",bg="black",fg="white", command=back_task, font=("Arial Bold",10))
folderButton.place(relx=0.5, rely=0.75, anchor=CENTER)

creditLabel = Label(mainWindow, text="Developed by Hashir K K during Gurugram Police Cyber Security Summer Internship 2020 under Rakshit Tandon ", font=("Arial",10) )
creditLabel.place(relx=0.5, rely= 1, anchor=S)

mainWindow.mainloop()
