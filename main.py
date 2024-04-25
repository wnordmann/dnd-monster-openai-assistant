from flask import Flask, request, send_from_directory, render_template
from flask_assets import Bundle, Environment
import os
import json
from AI import run_job
import re  # For a minor cleanup in ability descriptions

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  # Configure where to store uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Tailwind
assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css")
assets.register("css", css)
css.build()


@app.route('/')
def index():
    # Assuming 'index.html' in a 'templates' folder
    return render_template('index.html')


@app.route('/monster-maker', methods=['POST'])
def process_file():
    user_input = request.form['user_input']
    ai_result = run_job(user_input)

    monster_dict = json.loads(ai_result)

    formatted_stat_block = format_dnd_stat_block(monster_dict)
    # print(formatted_stat_block)

    return formatted_stat_block  # Return plain text

def format_dnd_stat_block(monster):
    """Formats the given monster dictionary into a D&D-style stat block with HTML."""

    stat_block = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{monster['name']} Stat Block</title>
        <style>
            /* Basic Styling */
            body {{ font-family: sans-serif; margin: 10px; }}
            .stat-block {{ border: 1px solid #ddd; padding: 10px; border-radius: 5px; display: flex; flex-direction: column; }}
            .stat-block h2 {{ text-align: center; }}
            .stat-info {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
            .stat-info > span:nth-child(1) {{ font-weight: bold; }}
            .abilities {{ display: flex; flex-wrap: wrap; margin-bottom: 10px; }}
            .ability {{ flex: 1; text-align: center; padding: 5px; margin: 2px; border: 1px solid #eee; border-radius: 3px; }}
            .ability span:nth-child(2) {{ font-weight: bold; }}
            .actions {{ border-top: 1px solid #ddd; padding-top: 10px; margin-top: 10px; }}
            .action {{ margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        <div class="stat-block">
            <h2>{monster['name']}</h2>
            <div class="stat-info"><span>Size</span><span>{monster['size']}, {monster['alignment']}</span></div>
            <div class="stat-info"><span>Armor Class</span><span>{monster['ac']} ({monster.get('armorType', '')})</span></div>
            <div class="stat-info"><span>Hit Points</span><span>{monster['hp']} ({monster['hpCalculation']})</span></div>
            <div class="stat-info"><span>Speed</span><span>{monster['speed']}</span></div>

            <div class="abilities">
                <div class="ability"><strong>STR</strong><br><span>{monster['str']} ({calculate_modifier(monster['str'])})</span></div>
                <div class="ability"><strong>DEX</strong><br><span>{monster['dex']} ({calculate_modifier(monster['dex'])})</span></div>
                <div class="ability"><strong>CON</strong><br><span>{monster['con']} ({calculate_modifier(monster['con'])})</span></div>
                <div class="ability"><strong>INT</strong><br><span>{monster['int']} ({calculate_modifier(monster['int'])})</span></div>
                <div class="ability"><strong>WIS</strong><br><span>{monster['wis']} ({calculate_modifier(monster['wis'])})</span></div>
                <div class="ability"><strong>CHA</strong><br><span>{monster['cha']} ({calculate_modifier(monster['cha'])})</span></div>
            </div>

            <div class="stat-info"><span>Saving Throws</span><span>{monster.get('savingThrows', '')}</span></div>
            <div class="stat-info"><span>Skills</span><span>{monster.get('skills', '')}</span></div>
            <div class="stat-info"><span>Damage Resistances</span><span>{monster.get('damageResistances', '')}</span></div>
            <div class="stat-info"><span>Damage Immunities</span><span>{monster.get('damageImmunities', '')}</span></div>
            <div class="stat-info"><span>Condition Immunities</span><span>{monster.get('conditionImmunities', '')}</span></div>
                        <div class="stat-info"><span>Senses</span><span>{monster.get('senses', '')}</span></div>
            <div class="stat-info"><span>Languages</span><span>{monster.get('languages', '')}</span></div>
            <div class="stat-info"><span>Challenge</span><span>{monster['challengeRating']}</span></div>

            <div class="properties">
                <h3>Properties</h3>
                {format_properties(monster.get('properties', []))}
            </div>
            <div class="actions">
                <h3>Actions</h3>
                {format_actions(monster.get('actions', []))}
            </div>
        </div>
    </body>
    </html>
    """  # Added closing </html> </body> tags
    return stat_block


def format_properties(properties):
    if not properties:
        return "None"  # If there are no properties

    formatted_properties = []
    for prop in properties:
        formatted_properties.append(
            f"<strong>{prop['name']}:</strong> {remove_extra_desc(prop['description'])}"
        )

    # Join properties with breaks for readability
    return "<br>".join(formatted_properties)


def format_actions(actions):
    if not actions:
        return "None"  # If there are no actions

    formatted_actions = []
    for action in actions:
        formatted_actions.append(
            f"<strong>{action['name']}:</strong> {remove_extra_desc(action['description'])}"
        )

    return "<br>".join(formatted_actions)


def remove_extra_desc(description):
    # A basic cleanup to remove "(Special Trait)" or similar notations
    return re.sub(r"\s+\([^()]]*\)", "", description).strip()


def calculate_modifier(ability_score):
    modifier = (ability_score - 10) // 2
    return f"+{modifier}" if modifier >= 0 else str(modifier)


def remove_extra_desc(description):
    # A basic cleanup to remove "(Special Trait)" or similar notations
    return re.sub(r"\s+\([^()]]*\)", "", description).strip()


if __name__ == '__main__':
    app.run(debug=True)
