from flask import Flask, request, render_template, redirect, flash, session, make_response, jsonify
from datetime import datetime
from surveys import Question, Survey, satisfaction_survey

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SECRET KEY'] =  app.secret_key


#  set a name for the  survey  session
sessions_for_survey =  "survey_session"

res_for_sessions  ="responses"
debug_for_sessions = "debug_info"

#Cookies time set to 40 days and name set
name_for_cookie = "Survey_Stat"
cookie_delim =  "<!>"
expiration_for_cookie =  3456000  
#  This will be the survey title borrowed from the class survey function
title = satisfaction_survey.title



def group_session_info(title_holder):
      # The session  holder  is responsible to hold  the  piece of  survey session
    session_holder = session[sessions_for_survey]
    responses = list(session_holder.get(res_for_sessions, []))
    responses.append(str(datetime.now()))
    responses.append(title_holder)
         # cookie data  consist with  cookies responses
    return {
        "cookie_data": (cookie_delim).join(responses),
        debug_for_sessions: session_holder.get(debug_for_sessions, False)
    }

def get_cookie_data():
    """ this () has the propesnity to read the  name of cookies
         it  will also  return  cookies data, responses,  title as well as last activity
    """

    cookie_data = request.cookies.get(name_for_cookie, "")
    cookie_data_holder = {"cookie_data_string": cookie_data}

    if (len(cookie_data) > 0):
        # cookie data is here 
        try:
            responses = cookie_data.split(cookie_delim)
            cookie_data_holder["title"] = responses.pop()
            cookie_data_holder["date_last_activity"] = responses.pop()
            date_obj = datetime.strptime(
                cookie_data_holder["date_last_activity"], "%Y-%m-%d %H:%M:%S.%f")
            cookie_data_holder["responses"] = responses
        except:
    
            cookie_data_holder["responses"] = []
    else:
        cookie_data_holder["responses"] = []

    return cookie_data_holder


def identify_cookie(debug_info):
    """  this () reads the read the name of cookies and perhaps activities 
    """

    cookie_data = get_cookie_data()
    cookie_info_holder = {"cookie_data": cookie_data["cookie_data_string"]}
    
    if (len(cookie_data.get("responses", [])) > 0):

        session_data = {
            res_for_sessions: cookie_data["responses"],
            debug_for_sessions: debug_info
        }

        datetime_obj = datetime.strptime(
            cookie_data["date_last_activity"], "%Y-%m-%d %H:%M:%S.%f")
        date_str = datetime_obj.strftime("%B %d, %Y at %I:%M %p")
        if (len(cookie_data["responses"]) == 4):
            cookie_info_holder["message"] = f" Your survey was completed on {date_str}. Click 'View Results' to see responses. "
            cookie_info_holder["button_holder"] = "View Results"
            cookie_info_holder["has_message"] = True
        else:
            cookie_info_holder["message"] = f"Survey was started on {date_str}. You may start from where you left. "
            cookie_info_holder["button_holder"] = "Resume Survey"
            cookie_info_holder["has_message"] = True

    else:
        cookie_info_holder["has_message"] = False
        cookie_info_holder["button_holder"] = "Start Survey"
        session_data = {
            res_for_sessions: [],
            debug_for_sessions: debug_info
        }

    session[sessions_for_survey] = session_data

    return  cookie_info_holder


def get_index():
    
    """ due to responses saved , get index number for next question """

    session_data = session[sessions_for_survey]

    return len(session_data.get(res_for_sessions, []))

 
    
    
# app.route links us to welcome page
@app.route("/")
def welcome_page():
    """
        the welcome page  has up to 3 funtions supported by render_template:
        1:  return title  of survey 
        2:  return  instructions
        3:  pass button_holder
        4:  starter information for  cookies
    """
    debug_info = request.args.get("debug", False)
    debug_info = True if (debug_info == "") else False

    instructions = satisfaction_survey.instructions

    start_info = identify_cookie(debug_info)
    if start_info.get("has_message", False):
        flash(start_info["message"], "msg")

    return render_template("welcomes.html", title_holder=title,
                           survey_instructions=instructions,
                           button_holder=start_info["button_holder"],
                           debug=debug_info,
                           name_of_session=sessions_for_survey,
                           cookie=start_info)
    
    
    
@ app.route("/session", methods=["POST"])
def setup_session():
    """ () checks to see if survey session exist else it will create one if not 
    exist.
    """

    try:
        session_data = session[sessions_for_survey]
        responses = session_data[res_for_sessions]

    except KeyError:
        
        responses = []
        session_data = {res_for_sessions: responses}
        session[sessions_for_survey] = session_data
            # To ask a question , number of res must be less than num of questions
    if (len(responses) < len(satisfaction_survey.questions)):
        return redirect("/questions")
    else:
        flash(
            f"You have completed our {title}. Here are the responses.", "warning")
        return redirect("/thankyou")

# @app.route link us to question form.html page
@app.route("/questions")
def questions_page():
    """ 
        In the question  page, the current question will be passed

        This page will display current question as well as answer choice
        button radios. 

        skipping next page on button radio will send a bad request to server

    """
    
    
    debug_info = request.args.get("debug", False)
    debug_info = True if (debug_info == "") else False

    quest_num = get_index()

    try:
        quest_holder = satisfaction_survey.questions[quest_num].question
    except IndexError:
        # it will show index  error if url is  not mishandled
      
        flash("This survey is completed. You cannot go back to the questions.", "warning")
        return redirect("/thankyou")

    #let get our answer by  making a choice from the class Question at chocies ()
    # in line 8 and the we can append  to the answers list
    answers_list = []
    x = 0
    for answer in satisfaction_survey.questions[quest_num].choices:
        answers_list.append((
            answer, f"{x}_{answer.replace(' ', '-')}"))
        x += 1

    session_info = group_session_info(title)
    if ((session_info.get(debug_for_sessions, False)) or (debug_info)):
        debug_info = True
    else:
        debug_info = False

    # in the form template we are passing the  title to title holder
     # we will pass the current  question to a question  number
     # we will pass all the  questions to  total quest
     # we will pass  question  to  a question holder
     # we will pass the  answers list  to  answer holder
     # we will pass tne debug info to debug varibale
     #we will pass the  session for  survey to the name of session
    html = render_template("form.html", title_holder=title,
                           quest_num=quest_num,
                           total_quest=(
                               len(satisfaction_survey.questions)),
                           quest_holder=quest_holder,
                           answer_holder=answers_list,
                           debug=debug_info,
                           name_of_session =sessions_for_survey,
                           cookie=session_info["cookie_data"])

    resp_obj = make_response(html)
    resp_obj.set_cookie(
        name_for_cookie, session_info["cookie_data"], expiration_for_cookie)
    return resp_obj

@app.route("/answer", methods=["POST"])
def answer_page():
    """ This function will handle answer to our survey questions. 

    """
      # survey session is passed to  session  data
      # we are requesting from <form action> and passing  answer 
      #  the answer are tagged along to the radio box name q-choices
    session_data = session[sessions_for_survey]
    responses = session_data.get(res_for_sessions, [])
    quest_num = len(session_data.get(res_for_sessions, []))

    answer = request.form[f'q-{quest_num}-choices']

    session_data[res_for_sessions].append(answer)
    session[sessions_for_survey] = session_data

     # If question is  no more we will redirect  to question  else say thanks!!
    if (len(responses) < len(satisfaction_survey.questions)):
        return redirect("/questions")
    else:
        return redirect("/thankyou")

@app.route("/thankyou")
def thank_you_page():
    """ thank you () handles thank you page.
    cookie and session  may be added by the debug at the bottom page and perhaps at 
    welcome page
    """
    
    debug_info = request.args.get("debug", False)
    debug_info = True if (debug_info == "") else False

    session_data = session[sessions_for_survey]
    responses = session_data.get(res_for_sessions, [])
    if (len(responses) == len(satisfaction_survey.questions)):
        quest_ans = "Your Survey Respond:<br>"
        x = 0
        for quest in satisfaction_survey.questions:
            quest_ans = f"{quest_ans}{x + 1}. {quest.question}  <b>{responses[x]}</b><br><br>"
            x +=  1

        session_info = group_session_info(title)
        if ((session_info.get(debug_for_sessions, False)) or (debug_info)):
            debug_info = True
        else:
             debug_info = False

        html = render_template("thanks.html", title_holder=title,
                               quest_ans_holder=quest_ans,
                               debug=debug_info,
                               name_of_session=sessions_for_survey,
                               cookie=session_info["cookie_data"])

        resp_obj = make_response(html)
        resp_obj.set_cookie(
            name_for_cookie, session_info["cookie_data"], expiration_for_cookie)
        return resp_obj

    else:
        # restart 
        # reset

        flash("There is a break in transmision!", "warning")
        return redirect("/questions")

   


@app.route("/reset")
def survey_reset():
    """ survey () reset completley reset survey and survey variables
    cookie will  be cleared for  each response
    """

    session[sessions_for_survey][res_for_sessions] = []
    reset_session = f' Survey is reset <br><br><a href="/">{title} welcome page</a>'
    # clear the cookie
    html = render_template("thanks.html", title_holder=title,
                           quest_ans=reset_session,
                           debug=True,
                           name_of_session=sessions_for_survey,
                           cookie="")

    resp_obj = make_response(html)
    resp_obj.set_cookie(name_for_cookie, "", expiration_for_cookie)
    return resp_obj

if __name__ == '__main__':
    app.debug = True
    app.run()