from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import os

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:

            # query to search for images
            query = request.form['content'].replace(" ","")

            #storing downloaded images
            save_folder = "images/"

             # create the directory if it doesn't exist
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)


             # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # fetch the search results page
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")


            # parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

             # find all img tags
            img_tags = soup.find_all("img")

            # download each image and save it to the specified directory
            del img_tags[0]
            img_mongo=[]

            for index,img_tag in enumerate(img_tags):
                # get the image source URL
                img_url = img_tag['src']
                #print(img_url)
                
                # send a request to the image URL and save the image
                img_data = requests.get(img_url).content
                img_dict = {"Index":index,"Image":img_url}
                img_mongo.append(img_dict)
                with open(os.path.join(save_folder, f"{query}_{img_tags.index(img_tag)}.jpg"), "wb") as f:
                    f.write(img_data)
            
            client = pymongo.MongoClient("mongodb+srv://shriji:shriji@cluster0.untzwu0.mongodb.net/?retryWrites=true&w=majority")
            db = client['image_scrap']    #creating a database
            scrap_col = db['image_scrap_data']   #creating a collection
            scrap_col.insert_many(img_mongo)          

            return render_template('result.html', img_mongo=img_mongo[0:(len(img_mongo)-1)])

        except Exception as e:
            logging.info(e)
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001)