from bs4 import BeautifulSoup
from tkinter import *
from PIL import ImageTk, Image
import requests, shutil, os

baseURI = "https://comic.naver.com/webtoon/detail.nhn" \
          "?titleId={titleId}&no={toonNo}&weekday={weekday}"

with open("sample.html", "wb+") as f:
    req_uri = baseURI.format(titleId=183559, toonNo=388, weekday="mon")
    r = requests.get(req_uri)

    f.write(r.text.encode("UTF-8"))

soup = BeautifulSoup(r.text, "html.parser")
elements = soup.select("div.wt_viewer > img")

"""
for elem in elements:
    _idx = elements.index(elem)

    _uri = elem['src']

    r = requests.get(_uri, stream=True, headers={"User-Agent": "Mozilla/5.0"})

    if r.status_code == 200:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, open(f"./img/{_idx}.png", "wb"))

"""


class MainWindow:
    def __init__(self, main):
        self.canvas = Canvas(main, relief=SUNKEN)
        self.button = Button(main, text="다음 페이지", command=self.onButton)
        sbarV = Scrollbar(main, orient=VERTICAL)
        sbarH = Scrollbar(main, orient=HORIZONTAL)

        sbarV.config(command=self.canvas.yview)
        sbarV.pack(side=RIGHT, fill=Y)

        sbarH.config(command=self.canvas.xview)
        sbarH.pack(side=BOTTOM, fill=X)

        self.canvas.config(width=600, height=1300)
        self.canvas.config(highlightthickness=0)
        self.canvas.config(yscrollcommand=sbarV.set)
        self.canvas.config(xscrollcommand=sbarH.set)

        self.button.pack(side="top")

        self.my_images = []

        for i in range(len(elements)):
            self.my_images.append(ImageTk.PhotoImage(file=f"./img/{i}.png"))

        self.my_image_number = 0

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=NW, image=self.my_images[self.my_image_number])

        width = self.my_images[self.my_image_number].width()
        height = self.my_images[self.my_image_number].height()

        self.canvas.config(scrollregion=(0, 0, width, height))

    def onButton(self):
        self.my_image_number += 1
        if self.my_image_number == len(self.my_images):
            self.my_image_number = 0

        self.canvas.itemconfig(self.image_on_canvas, image=self.my_images[self.my_image_number])


root = Tk()
MainWindow(root)
root.mainloop()
