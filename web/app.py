import sys
from flask import Flask, render_template
from flask import current_app
from sqlite_handler import SqliteHandler

sys.path.append(".")

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

last_update = "2024/01/02"  # todo  UPDATE THIS DATE AFTER EACH UPDATE

title = "Sejm Info"
sqlite_handler = SqliteHandler()
app.summaries = sqlite_handler.get_summaries()
app.poslowie_by_club, app.poslowie = sqlite_handler.get_poslowie()
app.sejm_term = 9

print(f"data has been loaded")


@app.route('/')
def index():
    return render_template("index.html", title=title, summaries=current_app.summaries)


@app.route('/poslowie')
def poslowie():
    return render_template("poslowie.html", title=title, clubs=current_app.poslowie_by_club)


@app.route('/poslowie/posel=<posel_id>')
def posel_details(posel_id):
    for posel in current_app.poslowie:
        if str(posel_id) == str(posel.get("id")):
            if len(posel.get("posel_id")) == 1:
                posel_id_formatted = f"00{posel.get('posel_id')}"
            elif len(posel.get("posel_id")) == 2:
                posel_id_formatted = f"0{posel.get('posel_id')}"
            elif len(posel.get("posel_id")) == 3:
                posel_id_formatted = f"{posel.get('posel_id')}"
            sejm_link = f"https://www.sejm.gov.pl/Sejm{current_app.sejm_term}.nsf/posel.xsp?id={posel_id_formatted}&type=P"
            voting_link = f"https://www.sejm.gov.pl/Sejm{current_app.sejm_term}.nsf/agent.xsp?symbol=POSELGL&NrKadencji={current_app.sejm_term}&Nrl={posel_id_formatted}"
            return render_template("poselDetails.html", title=title, posel=posel, sejm_link=sejm_link,
                                   voting_link=voting_link)


@app.route('/about')
def about():
    return render_template("about.html", title=title, last_update_date=last_update)


@app.route('/item=<item_id>')
def details(item_id):
    item_id = int(item_id)
    for s in current_app.summaries:
        if s["id"] == item_id:
            return render_template("details.html", item_id=item_id, title=title, summary=s["summary"],
                                   long_summary=s["long_summary"],
                                   project_id=s["project_id"], url=s["url"], process_url=s["process_url"],
                                   document_date=s["document_date"])
    return render_template("details.html", item_id=item_id, title=title, summary="N/A", url="N/A",
                           submitting_party=s["submitting_party"])


if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(host="0.0.0.0", debug=True, use_reloader=True, passthrough_errors=True, port=5000)
