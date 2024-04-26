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


@app.route('/spinner.svg')
def serve_loading_gif():
    return send_from_directory('static', 'spinner.svg')


@app.route('/monster-maker', methods=['POST'])
def process_file():
    user_input = request.form['user_input']
    print(f"Making a {user_input} monster")

    ai_result = run_job(user_input)

    monster_dict = json.loads(ai_result)

    formatted_stat_block = format_dnd_stat_block(monster_dict)

    return formatted_stat_block  # Return plain text


def format_dnd_stat_block(monster):
    """Formats the given monster dictionary into a D&D-style stat block with HTML."""

    stat_block = f"""
        <div class="stat-block wide">
        	<hr class="orange-border" />
            <div class="section-left">
                <div class="creature-heading">
                    <h1>{monster['name']}</h1>
                    <h2> {monster['size']}, {monster['alignment']} </h2>
                </div>
                <svg height="5" width="100%" class="tapered-rule">
                    <polyline points="0,0 400,2.5 0,5"></polyline>
                </svg>
                <div class="top-stats">
                    <div class="property-line first">
                        <h4>Armor Class</h4>
                        <p>{monster['ac']}</p>
                    </div> <!-- property line -->
                    <div class="property-line first">
                        <h4>Hit Points</h4>
                        <p>{monster['hp']} ({monster['hpCalculation']})</p>
                    </div> <!-- property line -->
                    <div class="property-line last">
                        <h4>Speed</h4>
                        <p>{monster['speed']}</p>
                    </div> <!-- property line -->
                    <svg height="5" width="100%" class="tapered-rule">
                        <polyline points="0,0 400,2.5 0,5"></polyline>
                    </svg>
                </div>
			    <div class="abilities">
                    <div class="ability-strength">
                        <h4>STR</h4>
                        <p>{monster['str']} ({calculate_modifier(monster['str'])})</p>
                    </div> <!-- ability strength -->
                    <div class="ability-dexterity">
                        <h4>DEX</h4>
                        <p>{monster['dex']} ({calculate_modifier(monster['dex'])})</p>
                    </div> <!-- ability dexterity -->
                    <div class="ability-constitution">
                        <h4>CON</h4>
                        <p>{monster['con']} ({calculate_modifier(monster['con'])})</p>
                    </div> <!-- ability constitution -->
                    <div class="ability-intelligence">
                        <h4>INT</h4>
                        <p>{monster['int']} ({calculate_modifier(monster['int'])})</p>
                    </div> <!-- ability intelligence -->
                    <div class="ability-wisdom">
                        <h4>WIS</h4>
                        <p>{monster['wis']} ({calculate_modifier(monster['wis'])})</p>
                    </div> <!-- ability wisdom -->
                    <div class="ability-charisma">
                        <h4>CHA</h4>
                        <p>{monster['cha']} ({calculate_modifier(monster['cha'])})</p>
                    </div> <!-- ability charisma -->
                </div> <!-- abilities -->
                <svg height="5" width="100%" class="tapered-rule">
                    <polyline points="0,0 400,2.5 0,5"></polyline>
                </svg>
                <div class="property-line first">
                    <h4>Damage Immunities</h4>
                    <p{monster.get('damageImmunities', '')}</p>
			    </div> <!-- property line -->
                <div class="property-line">
                    <h4>Condition Immunities</h4>
                    <p>{monster.get('conditionImmunities', '')}</p>
                </div> <!-- property line -->            
                <div class="property-line">
                    <h4>Senses</h4>
                    <p>{monster.get('senses', '')}</p>
                </div> <!-- property line -->
                <div class="property-line">
                    <h4>Languages</h4>
                    <p{monster.get('languages', '')}</p>
                </div> <!-- property line -->
                <div class="property-line">
                    <h4>Challenge Rating</h4>
                    <p>{monster.get('challengeRating', '')}</p>
                </div> <!-- property line -->
                <div class="property-line">
                    <h4>Saving Throws</h4>
                    <p>{monster.get('savingThrows', '')}</p>
                </div> <!-- property line -->
                <div class="property-line">
                    <h4>Skills</h4>
                    <p>{monster.get('skills', '')}</p>
                </div> <!-- property line -->
                <div class="property-line">
                    <h4>Damage Resistancees</h4>
                    <p>{monster.get('damageResistances', '')}</p>
                </div> <!-- property line -->
                <div class="property-line">
                    <h4>Damage Immunities</h4>
                    <p>{monster.get('damageImmunities', '')}</p>
                </div> <!-- property line -->
                <div class="property-line">
                    <h4>Condition Immunities</h4>
                    <p>{monster.get('conditionImmunities', '')}</p>
                </div> <!-- property line -->
                <svg height="5" width="100%" class="tapered-rule">
                    <polyline points="0,0 400,2.5 0,5"></polyline>
                </svg>
                <div class="property-block">
                    <h4>Properties</h4>
                    <p>{format_actions(monster.get('properties', []))}</p>
                </div>
            </div> <!-- section left -->
            <div class="section-right">            
                <div class="actions">
                    <h3>Fighting Style</h3>
                    <p>{monster.get('fightingStyle', '')}</p>
                </div>
                <div class="actions">
                    <h3>Actions</h3>
                    {format_actions(monster.get('actions', []))}
                </div>
                <!-- <div class="actions">
                    <h3>Legendary Actions</h3>
                    {format_actions(monster.get('legendaryActions', []))}
                </div> -->
            </div>
        </div>
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
    return "".join(formatted_properties)


def format_actions(actions):
    if not actions:
        return "None"  # If there are no actions

    formatted_actions = []
    for action in actions:
        formatted_actions.append(
            f"<div class='property-block'><h4>{action['name']}:</h4><p>{remove_extra_desc(action['description'])}</p></div>"
        )

    return "".join(formatted_actions)


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
