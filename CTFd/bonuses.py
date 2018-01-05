from flask import render_template, request, redirect, url_for, session, Blueprint, jsonify
from CTFd.models import db, Awards, Challenges, Keys, Solves, WrongKeys, Teams
from CTFd.challenges import chal, get_chal_class
from CTFd import utils
import json

bonuses = Blueprint('bonuses', __name__)


def bonus_view(teamid, message=""):
    bonuses = Solves.query.join(Challenges).filter(Solves.teamid == teamid, Challenges.type == 'bonus').all()

    return render_template('bonus.html', bonuses=bonuses, message=message)


@bonuses.route('/bonus', methods=['POST', 'GET'])
def submit_bonus_flag():
    if utils.authed():
        teamid = session['id']
        team = Teams.query.filter_by(id=session['id']).first()
        phantom_challenge = Challenges.query.filter(Challenges.type == 'bonus').first()
        chal_class = get_chal_class(phantom_challenge.type)

        if request.method == 'GET':
            return bonus_view(teamid, '')

        # Anti-bruteforce / submitting keys too quickly
        if utils.get_kpm(session['id']) > 10:
            if utils.ctftime():
                chal_class.fail(team=team, chal=phantom_challenge, request=request)
            return bonus_view(teamid, "You're submitting keys too fast. Slow down.")

        # Look for bonuses using this flag
        provided_key = request.form['key'].strip()
        bonus = Challenges.query.join(Keys, Keys.chal == Challenges.id).filter(Keys.flag == provided_key, Challenges.type == 'bonus' ).first()

        if bonus:
            submission = chal(bonus.id)
            verdict = json.loads(submission.response[0])
            return bonus_view(teamid, verdict['message'])
        else:
            chal_class.fail(team=team, chal=phantom_challenge, request=request)
            return bonus_view(teamid, 'Incorrect')

    else:
        return redirect(url_for('auth.login'))

