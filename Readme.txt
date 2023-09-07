0. set openAI api key in env variable
1. run sejm_parser (main.py) manually, it will update sqlite db with new records
a) it will backup previously downloaded files into zip
b) it will copy sqlite to the /web folder after it's done
2. restart web after that
3. new data will be served by the frontend


1. if links to sejm change - go to parser/sql_handler and links are built there.

---
sejm parser run
---
OPENAI_API_KEY='{key_here}' python main.py

IMPORTANT: install tesseract:

sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
sudo apt-get install tesseract-ocr-pol

---
CHAT GPT COST
---

summary of 45 files costs about 2$ (chat gpt 3.5 tubo)

---
DEPLOY
---
0. clone latest
1. root folder
2. run: `docker-compose down`
3. run: `docker-compose up -d --build`
