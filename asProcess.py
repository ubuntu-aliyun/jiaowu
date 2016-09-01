# coding: utf-8

from bs4 import BeautifulSoup
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def get_user(zjh, mm):
    user_dic = dict()
    user_dic['zjh'] = zjh
    user_dic['mm'] = mm

    return user_dic


def login(user_dic):
    indexurl = "http://zhjw.scu.edu.cn/loginAction.do"
    r = requests.post(indexurl, user_dic)
    title = BeautifulSoup(r.text, "html.parser").find("title").contents[0]
    if title == "学分制综合教务":
        return True, r.cookies
    else:
        return False, r.cookies


def get_xj_info(cook):
    xjurl = "http://zhjw.scu.edu.cn/xjInfoAction.do?oper=xjxx"
    r = requests.get(xjurl, cookies=cook)
    xj_key = BeautifulSoup(r.text, "html.parser").find_all("td", {"class": "fieldName"})
    xj_key = [i.text.strip() for i in xj_key]
    del xj_key[2]
    xj_value = BeautifulSoup(r.text, "html.parser").find_all("td", {"width": "275"})
    xj_value = [i.text.strip() for i in xj_value]
    xj_info = zip(xj_key, xj_value)
    return xj_info



def get_pj_info(cook):
    pjurl = "http://zhjw.scu.edu.cn/jxpgXsAction.do"
    r = requests.get(pjurl+"?oper=listWj&pageSize=300", cookies=cook)
    ret = BeautifulSoup(r.text, "html.parser")
    pj_info = [[], []]
    for item in ret.find_all("img", {"align": "center"}):
        if item.attrs["title"] == u"评估":
            pj_info[0].append(item.attrs["name"].split("#@"))
        else:
            pj_info[1].append(item.attrs["name"].split("#@"))

    return pj_info


def auto_pj(pj_info_0, pj_grade,cook):
    pjurl = "http://zhjw.scu.edu.cn/jxpgXsAction.do?oper=wjpg"
    for item, grade, pj_text in zip(pj_info_0, pj_grade[0], pj_grade[1]):
        if item[3] == u"学生评教":
            params_in = {
            "wjbm": item[0],
            "bpr": item[1],
            "pgnr": item[5],
            '0000000005': grade,
            '0000000006': grade,
            '0000000007': grade,
            '0000000008': grade,
            '0000000009': grade,
            '00000000010': grade,
            '00000000035': grade,
            "zgpj": pj_text.encode("gb2312")
            }
        else:
            params_in = {
                "wjbm": item[0],
                "bpr": item[1],
                "pgnr": item[5],
                '0000000028': grade,
                '0000000029': grade,
                '0000000030': grade,
                '0000000031': grade,
                '0000000032': grade,
                '00000000033': grade,
                "zgpj": pj_text.encode("gb2312")
            }
        for i in params_in.values():
            print i
        r = requests.post(pjurl, params_in, cookies=cook)
        print r.text



def get_pj(pj_info_1, cook):
    pjurl = "http://zhjw.scu.edu.cn/jxpgXsAction.do"
    for item in pj_info_1:
        params_in = {
            "wjbm": item[0],
            "bpr": item[1],
            "pgrn": item[5],
            "oper": "wjShow"
        }
        r = requests.post(pjurl, params_in, cookies=cook)
        ret = BeautifulSoup(r.text, "html.parser")
        params_in.clear()
        params_in["wjbm"] = item[0]
        params_in["bpr"] = item[1]
        params_in["pgnr"] = item[5]
        for i in ret.find_all("input", {"type": "radio"}):
            tmp_str = i.attrs["name"]
            if tmp_str not in params_in.keys():
                params_in[tmp_str] = i.attrs["value"]
        params_in["zgpj"] = u"很棒很好".encode("gb2312")
        r = requests.post(pjurl + "?oper=wjpg", params_in, cookies=cook)
        print r.text



def get_grade(cook):
    gradeurl = "http://zhjw.scu.edu.cn/gradeLnAllAction.do?type=ln&oper=sxinfo"
    r = requests.get(gradeurl, cookies=cook)
    grade_list = list()
    course_info = BeautifulSoup(r.text, "html.parser").find_all("tr", {"class": "odd"})
    for item in course_info:
        tmp_info = list()
        for i in item.text.split('\n'):
            if i.strip():
                tmp_info.append(i.strip())
        tmp_info[4] = float(tmp_info[4])
        try:
            tmp_info[6] = float(tmp_info[6])
        except:
            pass
        grade_list.append(tmp_info)
    return grade_list


def cal_grade(grade_list):
    cal_grade = [0.0, 0.0, 0.0, 0.0]  # 总体均分，总体绩点，必修均分，必修绩点
    credit_count = [0, 0, 0, 0, 0]  # 修读学分，已过学分, 必修学分, 选修学分,挂科数
    m_dict = {u"优秀": 95, u"良好": 85, u"中等": 75, u"通过": 60, u"及格": 60, u"合格": 0, u"未通过": 0, u"未及格": 0, u"未合格": 0}
    for item in grade_list:
        g = float(0)
        if isinstance(item[6], float):
            g = item[6]
        else:
            g = m_dict[item[6]]
        p = item[4]
        credit_count[0] += p
        credit_count[1] += p
        if item[5] == u"必修":
            credit_count[2] += p
            cal_grade[0] += g * p
            cal_grade[2] += g * p
            if g >= 95:
                cal_grade[1] += 4 * p
                cal_grade[3] += 4 * p
            elif g >= 90:
                cal_grade[1] += 3.8 * p
                cal_grade[3] += 3.8 * p
            elif g >= 85:
                cal_grade[1] += 3.6 * p
                cal_grade[3] += 3.6 * p
            elif g >= 80:
                cal_grade[1] += 3.2 * p
                cal_grade[3] += 3.2 * p
            elif g >= 75:
                cal_grade[1] += 2.7 * p
                cal_grade[3] += 2.7 * p
            elif g >= 70:
                cal_grade[1] += 2.2 * p
                cal_grade[3] += 2.2 * p
            elif g >= 65:
                cal_grade[1] += 1.7 * p
                cal_grade[3] += 1.7 * p
            elif g >= 60:
                cal_grade[1] += 1 * p
                cal_grade[3] += 1 * p
            else:
                credit_count[1] -= p
                credit_count[4] += 1
        else:
            credit_count[3] += p
            cal_grade[0] += g * p
            if g >= 95:
                cal_grade[1] += 4 * p
            elif g >= 90:
                cal_grade[1] += 3.8 * p
            elif g >= 85:
                cal_grade[1] += 3.6 * p
            elif g >= 80:
                cal_grade[1] += 3.2 * p
            elif g >= 75:
                cal_grade[1] += 2.7 * p
            elif g >= 70:
                cal_grade[1] += 2.2 * p
            elif g >= 65:
                cal_grade[1] += 1.7 * p
            elif g >= 60:
                cal_grade[1] += 1 * p
            else:
                cal_grade[0] += g * p  # 没过的选修不计入总分
                credit_count[1] -= p
                credit_count[3] -= p
                credit_count[4] += 1
    cal_grade[0] /= (credit_count[2] + credit_count[3])
    cal_grade[1] /= (credit_count[2] + credit_count[3])
    cal_grade[2] /= credit_count[2]
    cal_grade[3] /= credit_count[2]
    return cal_grade, credit_count





if __name__ == '__main__':
    user = get_user(sys.argv[1], sys.argv[2])
    login_flag, cook = login(user)
    pj_info = get_pj_info(cook)
    print pj_info
