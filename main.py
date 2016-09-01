# coding: utf-8

from flask import Flask, render_template, redirect, url_for, flash
from flask.ext.wtf import Form
from wtforms import RadioField, StringField, PasswordField, SubmitField, validators
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment

import asProcess


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = 'ni cai cai'


class UserForm(Form):
    user_account = StringField(u"学号：", validators=[validators.required()])
    password = PasswordField(u"密码：", validators=[validators.required()])
    submit = SubmitField(u"登陆")


class PJForm(Form):
    select_ = RadioField(choices=[("10_1", u"非常满意"), ("10_0.8", u"满意"), ("10_0.6", u"基本满意"), ("10_0.2", u"不满意")])
    text_ = StringField(u"")


class SubForm(Form):
    sub = SubmitField(u"一键评教")


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    global cook
    form = UserForm()
    if form.validate_on_submit():
        user_dic = dict()
        user_dic["zjh"] = form.user_account.data
        user_dic["mm"] = form.password.data
        form.user_account.data = ""
        form.password.data = ""
        login_flag, cook = asProcess.login(user_dic)
        if login_flag is True:
            return redirect(url_for("xjInfo", user=user_dic["zjh"], pwd=user_dic["mm"]))
        else:
            flash(u"学号或密码错误!")
    return render_template("login.html", form=form)


@app.route('/xjInfo/<user>/<pwd>')
def xjInfo(user, pwd):
    user_dic = dict()
    user_dic["zjh"] = user
    user_dic["mm"] = pwd
    login_flag, cook = asProcess.login(user_dic)
    if login_flag is False:
        flash(u"请先登录！")
        return redirect(url_for("index"))
    else:
        xj_info = asProcess.get_xj_info(cook)
        return render_template("xjInfo.html", xj_info=xj_info, user=user, pwd=pwd)


@app.route('/autoPJ/<user>/<pwd>', methods=["GET", "POST"])
def autoPJ(user, pwd):
    user_dic = dict()
    user_dic["zjh"] = user
    user_dic["mm"] = pwd
    login_flag, cook = asProcess.login(user_dic)
    if login_flag is False:
        flash(u"请先登录！")
        return redirect(url_for("index"))
    else:
        pj_info = asProcess.get_pj_info(cook)
        pj_form = list()
        sub = SubForm()
        for i in xrange(len(pj_info[0])):
            f = PJForm()
            f.select_.data = "10_1"
            f.text_.data = "很满意很好"
            pj_form.append(f)
        if len(pj_info[0]):
            if sub.is_submitted():
                pj_grade = [[], []]
                for item in pj_form:
                    pj_grade[0].append(item.select_.data)
                    pj_grade[1].append(item.text_.data)
                asProcess.get_pj(pj_info[0], cook)
            return redirect(url_for('autoPJ'))
        return render_template("autoPJ.html", pj_info=pj_info, pj_form=pj_form, len=len(pj_info[0]), sub=sub, user=user, pwd=pwd)


@app.route('/gradePoint/<user>/<pwd>')
def gradePoint(user, pwd):
    user_dic = dict()
    user_dic["zjh"] = user
    user_dic["mm"] = pwd
    login_flag, cook = asProcess.login(user_dic)
    if login_flag is False:
        flash(u"请先登录！")
        return redirect(url_for("index"))
    else:
        grade_list = asProcess.get_grade(cook)
        cal_grade, credit_count = asProcess.cal_grade(grade_list)
        return render_template("gradePoint.html", cal_grade=cal_grade, credit_count=credit_count,grade_list=grade_list, user=user, pwd=pwd)


if __name__ == '__main__':
    app.run(debug=False)
