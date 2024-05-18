
import numpy
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import joblib
text_clf = joblib.load('model_S.pkl')

logging.basicConfig(filename="scrapper.log", level=logging.INFO)


app = Flask(__name__)


@app.route("/", methods=['GET'])
def homepage():
    return render_template("main.html")


@app.route("/review", methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")

            bigboxes = flipkart_html.findAll(
                "div", {"class": "cPHDOP col-12-12"})  # "_1AtVbE col-12-12"})

            del bigboxes[0:3]
            box = bigboxes[0]
            try:
                productLink = "https://www.flipkart.com" + \
                    box.div.div.div.a['href']
            except:
                productLink = "https://www.flipkart.com" + \
                    box.div.div.div.div.a["hrf"]
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all(
                'div', {'class': "RcXBOT"})  # "_16PBlm"})

            reviews = []
            for commentbox in commentboxes:
                try:
                    product = flipkart_html.find_all(
                        "div", {"class": "KzDlHZ"})[0].text
                    # _1fQZEK
                    # _4rR01T

                except:

                    product = "na"
                    logging.info("product")

                try:
                    name = commentbox.div.div.find_all(
                        "p", {"class": "_2NsDsF AwS1CA"})[0].text

                except:
                    logging.info("name")
                    name = "no name found"

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'

                    logging.info(commentHead)

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text

                except Exception as e:
                    logging.info(e)

                    custComment = "N/A"

                try:
                    sentiment = text_clf.predict([custComment])[0]
                except:
                    sentiment = "Not avalible"

                mydict = {"Product": product, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment, "Sentiment": sentiment}
                reviews.append(mydict)

            logging.info("log my final maincss {}".format(reviews))

            return render_template('maincss.html', reviews=reviews[0:(len(reviews)-1)])

        except Exception as e:
            logging.info(e)
            error_message = 'Something is wrong with your flipkart product search. Please search any other product.'
            return render_template('ma.html', error_message=error_message)
    else:
        return render_template('ma.html')


# if __name__ == "__main__":
 #   app.run(host="0.0.0.0")
