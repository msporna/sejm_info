import datetime
import sys

from flask import Flask, render_template

from sqlite_handler import SqliteHandler

sys.path.append(".")

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

last_update = "2023/08/17"  # todo  UPDATE THIS DATE AFTER EACH UPDATE

title = "Sejm Info"
sqlite_handler = SqliteHandler()
summaries = sqlite_handler.get_summaries()


# print(json.dumps(summaries))


@app.route('/')
def index():
    return render_template("index.html", title=title, summaries=summaries)


@app.route('/about')
def about():
    return render_template("about.html", title=title, last_update_date=last_update)


@app.route('/item=<item_id>')
def details(item_id):
    item_id = int(item_id)
    for s in summaries:
        if s["id"] == item_id:
            return render_template("details.html", item_id=item_id, title=title, summary=s["summary"],
                                   project_id=s["project_id"], url=s["url"], process_url=s["process_url"],
                                   document_date=s["document_date"])
    return render_template("details.html", item_id=item_id, title=title, summary="N/A", url="N/A")


if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(host="0.0.0.0", debug=True, use_reloader=True, passthrough_errors=True, port=5000)
