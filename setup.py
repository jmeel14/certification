from . import actions

import notice

SETUP_TXT = {}

def search_setup_lines():
    file_ref = actions.commons.path.dirname(__file__) + actions.commons.path.sep + "setup_lines.txt"
    with open(file_ref, "r") as text_file:
        setup_text_raw = text_file.readlines()
        setup_text = []
        iter_lines = []
        for text in setup_text_raw:
            if(not "+" in text):
                iter_lines.append(text)
            else:
                iter_lines.append(text[0:text.index("+")])
                setup_text.append(iter_lines)
                iter_lines = []
        return setup_text

def target_setup_question(setup_text_dict, line_index):
    return ["".join(setup_text_dict[line_index][:-1]), setup_text_dict[line_index][-1]]

def ready_setup_lines():
    global SETUP_TXT
    pre_text = search_setup_lines()
    SETUP_TXT = {
        "welcome": "".join(pre_text[0]),
        "host": {
            "init": "".join(pre_text[1]),
            "addr": target_setup_question(pre_text, 2),
            "port": target_setup_question(pre_text, 3),
            "path": target_setup_question(pre_text, 4)
        },
        "org": {
            "init": "".join(pre_text[5]),
            "cname": target_setup_question(pre_text, 6),
            "o_name": target_setup_question(pre_text, 7),
            "ou_name": target_setup_question(pre_text, 8)
        },
        "pass": {
            "init": "".join(pre_text[9]),
            "passcode": target_setup_question(pre_text, 10)
        }
    }
def acquire_setup_answer(category, ref):
    question_val = input(SETUP_TXT[category][ref][0])
    if(question_val):
        print(SETUP_TXT[category][ref][1])
        return question_val

async def build_action(actions_list, answers_list, act_name, act_func, act_alias=None):
    """ Build an action used by the server.

        This function builds an action used by the server, and
        adds it to the server's action list.

        For every action that you may want to add, ensure that it either uses
        or is ready to accept the following arguments:
            req_conn: The connection to the client.
            req_data: The data received from the client.

        Args:
            act_name (str): The name of the action.
            act_func (function): The function to call when the action is called.
            act_data (dict): The data to pass to the function.
            act_alias (str): An alias that clients can communicate to request the action.
    """
    await actions.commons.assert_referable(actions_list, act_name, {
            "function": None, "data": act_func
        }
    )
    await actions.commons.assert_referable(answers_list, act_alias, {
        "function": None, "data": act_name
    })

    notice.gen_ntc("success", "title", """Action {0} has been built, with alias {1}.""".format(act_name, act_alias))

async def setup(cert_data, actions_list, answers_list):
    """Server setup function."""
    if not "is_set" in cert_data:
        ready_setup_lines()
        print(SETUP_TXT["welcome"])

        cert_data["host"] = {
            "addr": acquire_setup_answer("host", "addr"),
            "port": int(acquire_setup_answer("host", "port")),
            "path": acquire_setup_answer("host", "path")
        }
        cert_data["cert_metadata"] = {
            "auth": {
                "cname": acquire_setup_answer("org", "cname"),
                "org_name": acquire_setup_answer("org", "o_name"),
                "org_unit_name": acquire_setup_answer("org", "ou_name")
            }
        }
    action_list = [
        ["acknowledge", actions.requestor.acknowledge, "ack"],
        ["goodbye", actions.requestor.goodbye, "bye"],
        ["gen_cert", actions.certs.gen_cert, "gen"],
        ["write_key", actions.keys.write_priv_key, "key"]
    ]
    for action in action_list:
        await build_action(actions_list, answers_list, action[0], action[1], action[2])