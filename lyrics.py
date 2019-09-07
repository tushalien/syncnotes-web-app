import os
import sys
import urllib2
import urllib
import requests
import HTMLParser
import urllib2
import re

from flask import Flask
from flask import request,jsonify
from bs4 import BeautifulSoup
from datetime import datetime

from googleapiclient.discovery import build #pip install google-api-python-client
from oauth2client.tools import argparser #pip install oauth2client

reload(sys)  
sys.setdefaultencoding('utf8')

def fetch_srt(song_name,youtub_id):
	video_id=youtub_id
	#print song_name+" IN fetcj"
	if youtub_id=="":
		DEVELOPER_KEY = "AIzaSyDEEkM3B-LFQ2onli5s1O0BlhJ5xAUd8L4" 
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"

		query=song_name

		youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

		search_response = youtube.search().list(
		 q=query,
		 type="video",
		 part="id,snippet",
		 maxResults=1
		).execute()

		videos = {}

		# Add each result to the appropriate list, and then display the lists of
		 # matching videos.
		 # Filter out channels, and playlists.
		for search_result in search_response.get("items", []):
			if search_result["id"]["kind"] == "youtube#video":
			#videos.append("%s" % (search_result["id"]["videoId"]))
				videos[search_result["id"]["videoId"]] = search_result["snippet"]["title"]

		#print "Videos:\n", "\n".join(videos), "\n"

		s = ','.join(videos.keys())

		videos_list_response = youtube.videos().list(
			id=s,
			part='id,statistics'
			).execute()

		res = []
		for i in videos_list_response['items']:
			temp_res = dict(v_id = i['id'], v_title = videos[i['id']])
			temp_res.update(i['statistics'])
			video_id = temp_res['v_id']

		youtub_id = video_id

	#video_id="LYU-8IFcDPw"
	res = 'A'.join(str(ord(c)+13) for c in video_id)
	#print (video_id)
	res = res+"A"

	# opener.addheaders.append(('Cookie', 'ARRAffinity=d047cf032724053fc31b60286f444c5a97b5149595316dcb7d295fb1472d036a'))

	
	opener = urllib2.build_opener()

	# get cookie value 
	
	session = requests.session()
	url="https://extension.musixmatch.com"
	response = session.get(url,verify=False)
	cookie_value = session.cookies.get_dict()
	#print (cookie_value)
	opener.addheaders.append(('Host', "extension.musixmatch.com"))
	opener.addheaders.append(('Cookie', cookie_value))
	opener.addheaders.append(('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'))

	url = "https://extension.musixmatch.com/?res="+res+"&hl=en-US&v="+video_id+"&type=track&lang=en&name&kind&fmt=1"
	#print (url)
	f = opener.open("https://extension.musixmatch.com/?res="+res+"&hl=en-US&v="+video_id+"&type=track&lang=en&name&kind&fmt=1")
	f=f.read()

	h = HTMLParser.HTMLParser()
	cnt=0
	flag=0
	#f=f.read()
	s = f.split("text")
	str_name = "k.srt"

	srt_string = ""
	for i in s:
		if cnt%2==1:
			#print (i)
			flag  = flag+1
			srt_string = srt_string+str(flag)+"\n"

			s2 = i.split('"')
			c = h.unescape(s2[4])
			c2 = c[1:len(c)-2]
			#print (s2[1]+" "+s2[3]+" "+c2)
			end = float(s2[1])+float(s2[3])
			if "." in s2[1]:
				x1 = s2[1].split(".")
				ms1 = x1[1]
				while len(ms1)<3:
					ms1+="0"
				x = float(x1[0])
			else :
				ms1="000"
				x = float(s2[1])
			if "." in s2[3]:
				y1 = s2[3].split(".")
				ms2 = y1[1]
				while len(ms2)<3:
					ms2+="0"
				y = float(x1[0])
			else :
				ms2="000"
				y = float(s2[1])

			# process to end time

			end1= str(end)
			if "." in end1:
				x3 = end1.split(".")
				ms3 = x3[1]
				x4  = float(x3[0])
			else :
				ms3="000"
				x4 = float(end1)
			m, s = divmod(x, 60)
			h1, m = divmod(m, 60)

			# convert end time in ms,s,m,h format
			m2,s2 = divmod(x4,60)
			h2,m2 =divmod(m2,60)
			srt_string=srt_string+ ("%02d:%02d:%02d,%s --> %02d:%02d:%02d,%s" % (h1, m, s,ms1,h2,m2,s2,ms3))+"\n"
			srt_string=srt_string+c2+"\n\n"
			
		cnt = cnt+1
	return (srt_string,video_id)


def fetch_text(song,artist):

	try:
		search_term = artist + " " + song + " " + "metrolyrics" 
		search_term = urllib.quote(search_term)
		url = 'http://www.google.com/search?q='+search_term
		req = urllib2.Request(url, headers={'User-Agent' : "tushalien"})

		response = urllib2.urlopen(req)
		resp = response.read()
		resp = unicode(resp, errors='replace')

		result = resp.encode('utf8')

		link_start=result.find('http://www.metrolyrics.com')
		link_end=result.find('html',link_start+1)

		link = result[link_start:link_end+4]
		lyrics_html = urllib2.urlopen(link).read()
		soup = BeautifulSoup(lyrics_html)
		raw_lyrics= (soup.findAll('p', attrs={'class' : 'verse'}))

		lyrics=unicode.join(u'\n',map(unicode,raw_lyrics))
		lyrics= (lyrics.replace('<p class="verse">','\n'))
		lyrics=re.sub('<.*?>', '', lyrics)

		

		return lyrics
	except:
		pass

def fetch_subtitle(song):

	try:
		search_term = song
		print search_term

		search_term = urllib.quote(search_term)
		lyrics_html = urllib2.urlopen('http://music.baidu.com/search/lrc?key='+search_term).read()
		soup = BeautifulSoup(lyrics_html)
		raw_lyrics= (soup.findAll('a', attrs={'class' : 'down-lrc-btn'}))

		data=unicode.join(u'\n',map(unicode,raw_lyrics))
		test=data[34:]
		for i in range(0,len(test)):
				if test[i] == ".":
					final = test[:i]
					break

		final_url = "http://music.baidu.com/"+final+".lrc"
		urllib.urlretrieve(final_url, filename='x.lrc')
		filename='x.lrc'
		f = open(filename)
		output = []
		for line in f:
		    if not ":-" in line:
			output.append(line)
		f.close()
		f = open(filename, 'w')
		f.writelines(output)
		f.close()
		f = open(filename)
		output = []
		for line in f:
		    if not "00:00:00" in line:
			output.append(line)
		f.close()
		f = open(filename, 'w')
		f.writelines(output)
		f.close()
		with open(filename, 'r') as content_file:
		    content = content_file.read()

		for n in re.findall(ur'[\u4e00-\u9fff]+',content.decode("utf-8-sig")):
		    content= content.replace(n,'')

		f = open(filename, 'w')
		f.writelines(content)
		f.close()
		p = re.compile("[0-9]+")
		interval="100"

		lrc = open(filename)

		listtime =  []
		listlyrics = []

		for line in lrc.readlines():
		    if p.match(line.split(":")[0].replace("[","")):
			listtime.append("00:" + line.split("]")[0].replace("[","")+"0")
			listlyrics.append(line.split("]")[1])
		
		#read file and delete empty&useless lines

		o=""
		i=0

		while i <= listtime.__len__()-2:
		    o = o+\
		    str(i+1)+\
		    "\n"+\
		    listtime[i].replace(".",",")+\
		    " --> " +\
		    "0" + (str(datetime.strptime(listtime[i+1],"%H:%M:%S.%f")-datetime.strptime(interval,"%f"))).replace("000","").replace(".",",")+\
		    "\n"+listlyrics[i]+\
		    "\n"
		    i=i+1
		    
		o = o + str(i+1) + "\n" + listtime[-1].replace(".",",")+ " --> " + "\n" + listlyrics[-1] + "\n"
		return o
	except:
		pass
