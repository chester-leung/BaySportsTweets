import tweepy

# Consumer keys and access tokens, used for OAuth
#Taken out for privacy

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tweepy.API(auth)

# -------------- Events -------------------------------
def on_session_started(session_started_request, session):
    print("Starting new session.")

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
   want
   """
    # Dispatch to your skill's launch


    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetTweet":
        return get_team_tweet(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("Ending session.")

# ------------------- Functions that control the skill's behavior ---------------------
def get_welcome_response():
    session_attributes = {}
    card_title = "Bay Area Sports Tweets"
    speech_output = "Welcome to the Alexa Bay Area Sports Tweets skill. " \
                    "You can ask me for the most recent tweet from a Bay Area Sports team"
    reprompt_text = "Please ask me for the latest tweet from a Bay Area Sports Team, like the Warriors."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Bay Area Sports Tweets - Thanks"
    speech_output = "Thank you for using the Bay Sports Tweets skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_team_tweet(intent):
    card_title = "Most Recent Tweet"

    if "Team" in intent["slots"]:
        team_name = intent["slots"]["Team"]["value"]
        team_handle = get_team_handle(team_name)
        tweet = api.user_timeline(screen_name=team_handle, count=1)[0].text
        speech_output = "The " + team_name + " last tweeted, " + tweet
        card_title = team_name + "'s Most Recent Tweet"
    else:
        speech_output = "I'm not sure what team you're asking for. Please try again."

    reprompt_text = "You can ask me for another team's tweet by saying, for example, update me on the Giants."

    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))

def get_team_handle(team_name):
    team_name = team_name.upper()
    return {
        "GOLDEN STATE WARRIORS": "warriors",
        "DUBS": "warriors",
        "GOLDEN STATE": "warriors",
        "NINERS": "49ers",
        "SAN FRANCISCO 49ERS": "49ers",
        "FORTY NINERS": "49ers",
        "SAN FRANCISCO GIANTS": "SFGiants",
        "GIANTS": "SFGiants",
        "SAN JOSE SHARKS": "SanJoseSharks",
        "SHARKS": "SanJoseSharks",
        "OAKLAND A'S": "Athletics",
        "A'S": "Athletics",
        "EARTHQUAKES": "SJEarthquakes",
        "SAN JOSE EARTHQUAKES": "SJEarthquakes"
    }.get(team_name)

# ------------- Helpers to build JSON response -------------------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

# ------------------- Main handler ----------------------
def lambda_handler(event, context):
    """Entry Point"""
    if event["session"]["application"]["applicationId"] != "amzn1.ask.skill.5b80f255-b8dd-431e-a332-40e24aa57b38":
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])
