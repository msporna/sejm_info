import datetime
import os
import shutil
from time import sleep

import openai
import tiktoken
import concurrent.futures
import codecs


class TxtSummarizer:
    """
    openAi api key should be in environment variable!
    """

    def __init__(self):
        self.summarized = ""
        self.raw_summarized = []

    def process_pending_files(self):
        """
        load all files from "pending" and summarize
        :return:
        """
        print("starting to process text files with open ai...")
        contents = self.load_pending_txt_files()
        print(f"AI has to summarize {len(contents)} files...")
        files_ct = 1
        for content_raw in contents:
            print(f">>Summarizing {files_ct}/{len(contents)} [{(files_ct / len(contents)) * 100}%]")
            self.summarized = ""
            self.raw_summarized = []
            project_id = content_raw.get("pid")
            content = content_raw.get("content")
            # chunks = self.separate_into_chunks(content, 3000, 50)
            #
            # print(f">>Summarizing {project_id}....")
            # ct = 1
            # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            #     future_to_summary = {executor.submit(self.summarize, c): c for c in chunks}
            #     for future in concurrent.futures.as_completed(future_to_summary):
            #         print(f"completed summary {ct}")
            #         ct += 1
            #
            # print("summaries done, saving to file...")
            # file = codecs.open(f"download/twitter_lines/{project_id}.txt", "w", "utf-8")
            # for s in self.raw_summarized:
            #     file.write(s + "\n")
            # file.close()

            # final summary
            print("preparing the main summary")
            chunks = self.separate_into_chunks(content, 3000, 50)
            deeper_summary = ""
            for c in chunks:
                deeper_summary += " " + self.summarize(c,
                                                       prompt="Jesteś ekspertem od polityki w Polsce. Za chwilę wkleję ci tekst projektu ustawy lub uchwały nad którą pracuje sejm RP. Przeanalizuj i streść ogólny charakter dokumentu.",
                                                       max_tokens=600)
            print(">>> WHOLE SUMMARY TEXT:")
            print(deeper_summary)
            file = codecs.open(f"download/processed/{project_id}.txt", "w", "utf-8")
            file.write(deeper_summary)
            file.close()

            # hashtags
            chunks = self.separate_into_chunks(deeper_summary, 3000, 50)
            hash_tags = ""
            for c in chunks:
                hash_tags += " " + self.summarize(c,
                                                  prompt="Wygeneruj 3 hashtagi dla tekstu który za chwilę wkleję",
                                                  max_tokens=600)
            file = codecs.open(f"generated_hashtags/{project_id}.txt", "w", "utf-8")
            file.write(hash_tags)
            file.close()

            shutil.move(f"download/pending/{project_id}.txt",
                        f"download/processed_txt_files_archive/{project_id}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
            files_ct += 1
        print("completed summarizing")

    def load_pending_txt_files(self):
        dir = "download/pending"
        contents = []
        for filename in os.listdir(dir):
            f = os.path.join(dir, filename)
            if os.path.isfile(f):
                with open(f, 'r', encoding="utf-8") as file:
                    content = file.read()
                content = content.replace("\n", " ")
                if "_ustawa" in filename:
                    filename = filename.replace("_ustawa", "")
                elif "_uchwala" in filename:
                    filename = filename.replace("_uchwala", "")
                contents.append({"pid": filename.replace(".txt", ""), "content": content})
        return contents

    def separate_into_chunks(self, content, chunk_size, overlap):
        encoding = tiktoken.get_encoding('cl100k_base')
        tokens = encoding.encode(content)
        total_tokens = len(tokens)
        chunks = []
        raw_chunks = []
        for i in range(0, total_tokens, chunk_size - overlap):
            chunk = tokens[i:i + chunk_size]
            raw_chunks.append(chunk)
            chunks.append(encoding.decode(chunk))
        print(
            f"generated ${len(raw_chunks)} each has ${chunk_size} tokens so in total: ${len(raw_chunks) * chunk_size} tokens.")
        return chunks

    def summarize(self, input_text,
                  prompt="Jesteś ekspertem od polityki w Polsce. Za chwilę wkleję ci tekst projektu ustawy lub uchwały nad którą pracuje sejm RP. Przeanalizuj i streść ogólny charakter dokumentu. Napisz o czym jest ten projekt i zrób to zwięźle bym mógł opublikować to w 1 tweecie (max 150 znaków).",
                  max_tokens=150):
        """
        https://platform.openai.com/docs/api-reference/completions/object
        :param input_text:
        :return:
        """
        sleep(3)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": input_text}],
                temperature=0.1,
                max_tokens=max_tokens
            )
        except:
            # retry
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": input_text}],
                temperature=0.1,
                max_tokens=max_tokens
            )
        summary = response.choices[0].message.content
        print(summary)
        self.summarized += summary
        self.raw_summarized.append(summary)
        return summary
